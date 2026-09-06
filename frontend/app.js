const form = document.querySelector("#evaluation-form");
const ideaInput = document.querySelector("#idea");
const button = document.querySelector("#submit-button");
const errorMessage = document.querySelector("#error-message");
const emptyState = document.querySelector("#empty-state");
const loadingState = document.querySelector("#loading-state");
const resultCard = document.querySelector("#result-card");
const score = document.querySelector("#score");
const verdict = document.querySelector("#verdict");
const recommendation = document.querySelector("#recommendation");
const sourcesList = document.querySelector("#sources-list");

function setState(state) {
  emptyState.classList.toggle("hidden", state !== "empty");
  loadingState.classList.toggle("hidden", state !== "loading");
  resultCard.classList.toggle("hidden", state !== "result");
}

function setVerdict(value) {
  verdict.textContent = value;
  verdict.className = "verdict";
  if (value === "GO") {
    verdict.classList.add("go");
  }
  if (value === "NO-GO") {
    verdict.classList.add("no-go");
  }
}

function renderSources(sources) {
  sourcesList.innerHTML = "";

  if (!sources.length) {
    const item = document.createElement("li");
    item.textContent = "No sources returned.";
    sourcesList.append(item);
    return;
  }

  for (const source of sources.slice(0, 3)) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    const summary = document.createElement("p");

    link.href = source.url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = source.title || source.url;
    summary.textContent = source.summary || "No summary available.";

    item.append(link, summary);
    sourcesList.append(item);
  }
}

function renderResult(data) {
  score.textContent = `${data.final_score}/100`;
  setVerdict(data.verdict);
  recommendation.textContent = data.recommendation;
  renderSources(data.research_sources || []);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const idea = ideaInput.value.trim();
  if (!idea) {
    errorMessage.textContent = "Enter a startup idea first.";
    return;
  }

  errorMessage.textContent = "";
  button.disabled = true;
  button.textContent = "Evaluating...";
  setState("loading");

  try {
    const response = await fetch("/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea }),
    });

    if (!response.ok) {
      throw new Error("Evaluation failed.");
    }

    const data = await response.json();
    renderResult(data);
    setState("result");
  } catch (error) {
    errorMessage.textContent = error.message;
    setState("empty");
  } finally {
    button.disabled = false;
    button.textContent = "Evaluate idea";
  }
});
