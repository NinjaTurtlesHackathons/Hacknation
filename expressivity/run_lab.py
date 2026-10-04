"""Run the framework's lab loop (asd.lab_loop) for this domain with a robust JSON parser for LLM answers.

asd.llm.ask_json raises json.JSONDecodeError (not LLMError) when an answer contains extra text after the JSON object; the lab loop
only catches LLMError, so one malformed cached answer stops the loop permanently (lab round 1, decision EX9). The shared core is
not edited (each role writes only its own files); this wrapper parses the first JSON object (json.JSONDecoder.raw_decode) and turns
remaining parse failures into LLMError, which the loop handles as designed.
  python -m expressivity.run_lab --domain expressivity --recherche --runden 10 --budget-usd 25 --fragen expressivity/questions.json
"""
import json, re, sys
import asd.llm as L


def robust_ask_json(prompt, system="Du bist ein sorgfältiger Wissenschaftler. Antworte nur mit gültigem JSON.", **kw):
    text = L.ask(prompt, system, **kw)
    m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.S)
    cands = [m.group(1)] if m else []
    cands += [text[i:] for i in [j for j, ch in enumerate(text) if ch in "{["][:5]]
    for c in cands:
        try:
            obj, _ = json.JSONDecoder().raw_decode(c)
            return obj
        except json.JSONDecodeError:
            continue
    raise L.LLMError(f"no parsable JSON in answer: {text[:200]}")


L.ask_json = robust_ask_json
import asd.lab_loop as LL, asd.discovery as DI, asd.research as RS   # noqa: E402
LL.ask_json = DI.ask_json = RS.ask_json = robust_ask_json

if __name__ == "__main__":
    LL.main()
