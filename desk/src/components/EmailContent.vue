<template>
  <iframe
    ref="iframeRef"
    :srcdoc="htmlContent"
    class="prose-f block h-10 max-h-[500px] w-full"
  />
</template>

<script setup lang="ts">
import { getFontFamily } from "@/utils";
import { computed, ref, watch } from "vue";

const props = defineProps({
  content: {
    type: String,
    required: true,
  },
});

const iframeRef = ref<HTMLIFrameElement | null>(null);
const _content = ref(props.content);

const parser = new DOMParser();
const doc = parser.parseFromString(_content.value, "text/html");

const gmailReplyToContent = doc.querySelectorAll("div.gmail_quote");
const outlookReplyToContent = doc.querySelectorAll("div#appendonsend");
const replyToContent = doc.querySelectorAll("p.reply-to-content");

if (gmailReplyToContent.length) {
  _content.value = parseReplyToContent(doc, "div.gmail_quote", true);
} else if (outlookReplyToContent.length) {
  _content.value = parseReplyToContent(doc, "div#appendonsend");
} else if (replyToContent.length) {
  _content.value = parseReplyToContent(doc, "p.reply-to-content");
}

function parseReplyToContent(
  doc: Document,
  selector: string,
  forGmail = false
) {
  function handleAllInstances(doc: Document) {
    const replyToContentElements = doc.querySelectorAll(selector);
    if (replyToContentElements.length === 0) return;
    const replyToContentElement = replyToContentElements[0];
    replaceReplyToContent(replyToContentElement, forGmail);
    handleAllInstances(doc);
  }

  handleAllInstances(doc);
  return doc.body.innerHTML;
}

function replaceReplyToContent(
  replyToContentElement: Element,
  forGmail: boolean
) {
  if (!replyToContentElement) return;
  const randomId = Math.random().toString(36).substring(2, 7);
  const wrapper = doc.createElement("div");
  wrapper.classList.add("replied-content");

  const collapseLabel = doc.createElement("label");
  collapseLabel.classList.add("collapse");
  collapseLabel.setAttribute("for", randomId);
  collapseLabel.innerHTML = "...";
  wrapper.appendChild(collapseLabel);

  const collapseInput = doc.createElement("input");
  collapseInput.setAttribute("id", randomId);
  collapseInput.setAttribute("class", "replyCollapser");
  collapseInput.setAttribute("type", "checkbox");
  wrapper.appendChild(collapseInput);

  if (forGmail) {
    const prevSibling = replyToContentElement.previousElementSibling;
    if (prevSibling && prevSibling.tagName === "BR") {
      prevSibling.remove();
    }
    const cloned = replyToContentElement.cloneNode(true) as Element;
    cloned.classList.remove("gmail_quote");
    wrapper.appendChild(cloned);
  } else {
    const allSiblings = Array.from(
      replyToContentElement.parentElement?.children || []
    );
    const replyToContentIndex = allSiblings.indexOf(replyToContentElement);
    const followingSiblings = allSiblings.slice(replyToContentIndex + 1);

    if (followingSiblings.length === 0) return;

    const clonedFollowingSiblings = followingSiblings.map((sibling) =>
      sibling.cloneNode(true)
    );

    const div = doc.createElement("div");
    div.append(...clonedFollowingSiblings);
    wrapper.append(div);

    for (let i = replyToContentIndex + 1; i < allSiblings.length; i++) {
      replyToContentElement.parentElement?.removeChild(allSiblings[i]);
    }
  }

  replyToContentElement.parentElement?.replaceChild(
    wrapper,
    replyToContentElement
  );
}

const htmlContent = computed(
  () => `
  <!DOCTYPE html>
  <html>
  <head>
    <base target="_blank" />
    <style>
      * {
        margin: 0;
        padding: 0;
      }
      body {
        color: #1f2937;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 14px;
        line-height: 1.5;
      }
      .replied-content .collapse {
        margin: 10px 0 10px 0;
        visibility: visible;
        cursor: pointer;
        display: flex;
        font-size: larger;
        font-weight: 700;
        height: 12px;
        line-height: 0.1;
        background: #e8eaed;
        width: 23px;
        justify-content: center;
        border-radius: 5px;
      }
      .replied-content .collapse:hover {
        background: #dadce0;
      }
      .replied-content .collapse + input {
        display: none;
      }
      .replied-content .collapse + input + div {
        display: none;
      }
      .replied-content .collapse + input:checked + div {
        display: block;
      }
      .email-content {
        word-break: break-word;
      }
      .email-content a {
        color: #2563eb;
        text-decoration: underline;
      }
      .email-content table {
        table-layout: auto;
      }
      .email-content img {
        max-width: 100%;
        height: auto;
      }
    </style>
  </head>
  <body>
    <div class="email-content">${_content.value}</div>
  </body>
  </html>
  `
);

watch(iframeRef, (iframe) => {
  if (iframe) {
    iframe.onload = () => {
      const emailContent =
        iframe.contentWindow?.document.querySelector(".email-content");
      if (!emailContent) return;

      const parent = emailContent.closest("html");
      if (!parent) return;

      emailContent.classList.add(getFontFamily(_content.value));
      iframe.style.height = parent.offsetHeight + 1 + "px";

      const replyCollapsers = emailContent.querySelectorAll(".replyCollapser");
      if (replyCollapsers.length) {
        replyCollapsers.forEach((replyCollapser) => {
          replyCollapser.addEventListener("change", () => {
            iframe.style.height = parent.offsetHeight + 1 + "px";
          });
        });
      }
    };
  }
});
</script>
