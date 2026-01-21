import argparse
import csv
import json
import re
import time
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://easyoffer.ru/python-developer/questions"
DEFAULT_INTERVIEW_TYPE = "tehnicheskoe"


@dataclass(frozen=True)
class QuestionRow:
    page: int
    question: str
    chance: str


def build_url(page: int, interview_type: str) -> str:
    query = urlencode({"interviewType": interview_type, "page": page})
    return f"{BASE_URL}?{query}"


def fetch_html(url: str, timeout: float = 20.0) -> str:
    # Используем явный User-Agent, чтобы получить обычную HTML-страницу
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; AIDD-MVP-Scraper/1.0)"})
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def iter_script_blocks(html: str) -> Iterator[str]:
    # Извлекаем содержимое script-тегов
    for match in re.finditer(r"<script[^>]*>(.*?)</script>", html, flags=re.DOTALL | re.IGNORECASE):
        content = match.group(1).strip()
        if content:
            yield content


def extract_json_from_assignment(text: str) -> List[Any]:
    # Ищем присваивания вида window.__STATE__ = {...};
    results: List[Any] = []
    for m in re.finditer(r"window\.__[A-Z0-9_]+__\s*=\s*", text):
        start = m.end()
        extracted = extract_json_object(text, start)
        if extracted:
            try:
                results.append(json.loads(extracted))
            except json.JSONDecodeError:
                continue
    return results


def extract_json_object(text: str, start_index: int) -> Optional[str]:
    # Пытаемся выделить JSON-объект или массив по скобочному балансу
    if start_index >= len(text):
        return None
    opener = text[start_index]
    if opener not in ("{", "["):
        return None
    stack = [opener]
    for i in range(start_index + 1, len(text)):
        ch = text[i]
        if ch in ("{", "["):
            stack.append(ch)
        elif ch in ("}", "]"):
            stack.pop()
            if not stack:
                return text[start_index : i + 1]
    return None


def extract_json_blocks(html: str) -> List[Any]:
    # Сначала ищем __NEXT_DATA__ (Next.js), затем другие JSON-вставки
    blocks: List[Any] = []
    next_data = re.search(
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if next_data:
        try:
            blocks.append(json.loads(next_data.group(1)))
        except json.JSONDecodeError:
            pass
    for script in iter_script_blocks(html):
        blocks.extend(extract_json_from_assignment(script))
    return blocks


def iter_dicts(obj: Any) -> Iterator[dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from iter_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_dicts(item)


def extract_questions_from_json(blocks: Iterable[Any]) -> List[QuestionRow]:
    question_keys = ("question", "title", "text")
    chance_keys = ("chance", "probability", "rate", "percent", "percentage")
    results: List[QuestionRow] = []

    for block in blocks:
        for item in iter_dicts(block):
            question_value = None
            chance_value = None
            for key in question_keys:
                if key in item and isinstance(item[key], str):
                    question_value = item[key].strip()
                    break
            for key in chance_keys:
                if key in item and isinstance(item[key], (str, int, float)):
                    chance_value = str(item[key]).strip()
                    break
            if question_value and chance_value:
                results.append(QuestionRow(page=0, question=question_value, chance=chance_value))

    return results


def try_parse_html(html: str) -> List[QuestionRow]:
    blocks = extract_json_blocks(html)
    return extract_questions_from_json(blocks)


def parse_with_playwright(
    url: str,
    card_selector: Optional[str],
    question_selector: Optional[str],
    chance_selector: Optional[str],
    timeout_ms: int,
) -> List[QuestionRow]:
    # Playwright используется только если доступен в окружении
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright не установлен. Установите или используйте JSON-парсинг.") from exc

    results: List[QuestionRow] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)

        if card_selector and question_selector and chance_selector:
            cards = page.locator(card_selector)
            for idx in range(cards.count()):
                card = cards.nth(idx)
                question = card.locator(question_selector).inner_text().strip()
                chance = card.locator(chance_selector).inner_text().strip()
                if question and chance:
                    results.append(QuestionRow(page=0, question=question, chance=chance))
        else:
            # Эвристика: ищем элементы с процентом, затем берем ближайший текст вопроса
            rows = page.evaluate(
                """
                () => {
                    const percentRe = /\\d+\\s*%/;
                    const candidates = [];
                    const all = Array.from(document.querySelectorAll("*"));
                    for (const el of all) {
                        const text = (el.textContent || "").trim();
                        if (!percentRe.test(text)) continue;
                        const chanceMatch = text.match(percentRe);
                        if (!chanceMatch) continue;
                        // Попробуем найти текст вопроса рядом
                        let question = "";
                        let container = el;
                        for (let i = 0; i < 4 && container; i++) {
                            if (container.querySelector) {
                                const q = container.querySelector("a, h3, h4, h5, .question, .title");
                                if (q && q.textContent) {
                                    question = q.textContent.trim();
                                    break;
                                }
                            }
                            container = container.parentElement;
                        }
                        if (question) {
                            candidates.push({question, chance: chanceMatch[0]});
                        }
                    }
                    return candidates;
                }
                """
            )
            for item in rows:
                question = str(item.get("question", "")).strip()
                chance = str(item.get("chance", "")).strip()
                if question and chance:
                    results.append(QuestionRow(page=0, question=question, chance=chance))

        browser.close()

    return results


def fetch_page_questions(
    page_num: int,
    interview_type: str,
    use_playwright: bool,
    card_selector: Optional[str],
    question_selector: Optional[str],
    chance_selector: Optional[str],
    timeout_ms: int,
) -> List[QuestionRow]:
    url = build_url(page_num, interview_type)
    html = fetch_html(url)
    rows = try_parse_html(html)
    if rows:
        return [QuestionRow(page=page_num, question=row.question, chance=row.chance) for row in rows]
    if use_playwright:
        rows = parse_with_playwright(url, card_selector, question_selector, chance_selector, timeout_ms)
        return [QuestionRow(page=page_num, question=row.question, chance=row.chance) for row in rows]
    raise RuntimeError(
        "Не удалось извлечь данные из HTML. "
        "Возможно, страница рендерится JS. Запустите с --use-playwright."
    )


def write_csv(rows: Iterable[QuestionRow], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["page", "question", "chance"])
        for row in rows:
            writer.writerow([row.page, row.question, row.chance])


def main() -> int:
    parser = argparse.ArgumentParser(description="Парсер вопросов и шанса с easyoffer.ru")
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--end-page", type=int, default=160)
    parser.add_argument("--interview-type", type=str, default=DEFAULT_INTERVIEW_TYPE)
    parser.add_argument("--out", type=str, default="easyoffer_questions.csv")
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--use-playwright", action="store_true")
    parser.add_argument("--card-selector", type=str, default=None)
    parser.add_argument("--question-selector", type=str, default=None)
    parser.add_argument("--chance-selector", type=str, default=None)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    args = parser.parse_args()

    all_rows: List[QuestionRow] = []
    for page_num in range(args.start_page, args.end_page + 1):
        try:
            page_rows = fetch_page_questions(
                page_num=page_num,
                interview_type=args.interview_type,
                use_playwright=args.use_playwright,
                card_selector=args.card_selector,
                question_selector=args.question_selector,
                chance_selector=args.chance_selector,
                timeout_ms=args.timeout_ms,
            )
            all_rows.extend(page_rows)
            print(f"[OK] page={page_num} rows={len(page_rows)}")
        except (HTTPError, URLError, RuntimeError) as exc:
            print(f"[ERR] page={page_num} error={exc}")
        time.sleep(max(0.0, args.sleep))

    write_csv(all_rows, args.out)
    print(f"[DONE] rows={len(all_rows)} file={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
