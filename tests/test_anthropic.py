import pytest
from unittest.mock import AsyncMock, patch
import chapito.anthropic_chat as anthropic_chat


@pytest.mark.asyncio
async def test_send_request_and_get_response():
    # Arrange
    mock_tab = AsyncMock()
    mock_element = AsyncMock()
    mock_tab.find.return_value = mock_element
    mock_tab.query.return_value = [mock_element]
    mock_element.outer_html = "<html><body>Mocked response</body></html>"

    message = "Hello, world!"

    # Act
    with patch('chapito.anthropic_chat.transfer_prompt', new_callable=AsyncMock):
        await anthropic_chat.send_request_and_get_response(mock_tab, message)

    # Assert
    mock_tab.find.assert_any_call(css_selector="div[contenteditable='true']", timeout=10)
    mock_tab.find.assert_any_call(css_selector=anthropic_chat.SUBMIT_CSS_SELECTOR, timeout=anthropic_chat.TIMEOUT_SECONDS)
    mock_element.click.assert_awaited()
    mock_tab.find.assert_any_call(css_selector=anthropic_chat.SUBMIT_DISABLE_CSS_SELECTOR, timeout=anthropic_chat.TIMEOUT_SECONDS)
    mock_tab.query.assert_awaited_with(xpath=anthropic_chat.ANSWER_XPATH)


def test_clean_chat_answer() -> None:
    html = """
<div class="font-claude-message  relative  leading-[1.65rem]  [&amp;_pre>div]:bg-bg-300  [&amp;_.ignore-pre-bg>div]:bg-transparent [&amp;>div>div>:is(p,ul,ol)]:pr-4 md:[&amp;>div>div>:is(p,ul,ol)]:pr-8"><div><div class="grid-cols-1 grid gap-2.5 [&amp;_>_*]:min-w-0"><p class="whitespace-pre-wrap break-words">index.html</p>
<pre><div class="relative flex flex-col rounded-lg"><div class="text-text-300 absolute pl-3 pt-2.5 text-xs"></div><div class="pointer-events-none sticky my-0.5 ml-0.5 flex items-center justify-end px-1.5 py-1 mix-blend-luminosity top-0"><div class="from-bg-300/90 to-bg-300/70 pointer-events-auto rounded-md bg-gradient-to-b p-0.5 backdrop-blur-md"><button class="flex flex-row items-center gap-1 rounded-md p-1 py-0.5 text-xs transition-opacity delay-100 text-text-300 hover:bg-bg-200 opacity-60 hover:opacity-100" data-state="closed"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 256 256" class="text-text-500 mr-px -translate-y-[0.5px]"><path d="M200,32H163.74a47.92,47.92,0,0,0-71.48,0H56A16,16,0,0,0,40,48V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm-72,0a32,32,0,0,1,32,32H96A32,32,0,0,1,128,32Zm72,184H56V48H82.75A47.93,47.93,0,0,0,80,64v8a8,8,0,0,0,8,8h80a8,8,0,0,0,8-8V64a47.93,47.93,0,0,0-2.75-16H200Z"></path></svg><span class="text-text-200 pr-0.5">Copy</span></button></div></div><div><div class="prismjs code-block__code !my-0 !rounded-lg !text-sm !leading-relaxed"><code style="background: rgb(40, 44, 52); color: rgb(171, 178, 191); text-shadow: rgba(0, 0, 0, 0.3) 0px 1px; font-family: &quot;Fira Code&quot;, &quot;Fira Mono&quot;, Menlo, Consolas, &quot;DejaVu Sans Mono&quot;, monospace; direction: ltr; text-align: left; white-space: pre; word-spacing: normal; word-break: normal; line-height: 1.5; tab-size: 2; hyphens: none;"><span class=""><span class="">&lt;!DOCTYPE html&gt;
</span></span><span class="">&lt;html lang="fr"&gt;
</span><span class="">&lt;head&gt;
</span><span class="">    &lt;meta charset="UTF-8"&gt;
</span><span class="">    &lt;title&gt;Bonjour&lt;/title&gt;
</span><span class="">    &lt;style&gt;
</span><span class="">        body {
</span><span class="">            background-color: black;
</span><span class="">            color: white;
</span><span class="">        }
</span><span class="">    &lt;/style&gt;
</span><span class="">&lt;/head&gt;
</span><span class="">&lt;body&gt;
</span><span class="">    &lt;h1&gt;Bonjour!&lt;/h1&gt;
</span><span class="">&lt;/body&gt;
</span><span class="">&lt;/html&gt;</span></code></div></div></div></pre>
<p class="whitespace-pre-wrap break-words">J'ai ajouté un élément <code class="bg-text-200/5 border border-0.5 border-border-300 text-danger-000 whitespace-pre-wrap rounded-[0.3rem] px-1 py-px text-[0.9rem]">&lt;style&gt;</code> dans la section <code class="bg-text-200/5 border border-0.5 border-border-300 text-danger-000 whitespace-pre-wrap rounded-[0.3rem] px-1 py-px text-[0.9rem]">&lt;head&gt;</code> qui définit un fond noir (<code class="bg-text-200/5 border border-0.5 border-border-300 text-danger-000 whitespace-pre-wrap rounded-[0.3rem] px-1 py-px text-[0.9rem]">background-color: black;</code>) et du texte blanc (<code class="bg-text-200/5 border border-0.5 border-border-300 text-danger-000 whitespace-pre-wrap rounded-[0.3rem] px-1 py-px text-[0.9rem]">color: white;</code>) pour tout le corps de la page.</p></div></div></div>
"""

    expected = """
index.html
```
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Bonjour</title>
    <style>
        body {
            background-color: black;
            color: white;
        }
    </style>
</head>
<body>
    <h1>Bonjour!</h1>
</body>
</html>
```

J'ai ajouté un élément `<style>` dans la section `<head>` qui définit un fond noir (`background-color: black;`) et du texte blanc (`color: white;`) pour tout le corps de la page.
"""

    assert anthropic_chat.clean_chat_answer(html) == expected.strip()
