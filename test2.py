import re

if __name__ == "__main__":
    extract_text = re.compile(r"(?P<text>([^\[]|\[\[)*)(?P<rest>.*)")
    extract_tag = re.compile(r"\[(?P<tag>[^\]]*)\](?P<rest>.*)")
    s = "asds[asasf]dfsdf[afasf]asdsa[/afasf]asdad[asds][/][/]"
    print(f"s={s}")
    tag_stack = []
    while s:
        m = extract_text.match(s)
        text = m.group("text")
        if text:
            print(f"[{' '.join(set(tag_stack))}] {text}")
        s = m.group("rest")
        if s:
            m = extract_tag.match(s)
            tag = m.group("tag")
            if tag:
                if tag.startswith("/"):
                    assert tag[1:] in ["", tag_stack[-1]]
                    tag_stack.pop(-1)
                else:
                    tag_stack.append(tag)
            s = m.group("rest")
    assert not tag_stack
