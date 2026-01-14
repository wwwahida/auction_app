<template>
  <div class="card shadow-sm mt-4">
    <div class="card-body">
      <h5 class="mb-3">Questions</h5>

      <div v-if="loading" class="text-muted">Loading questions…</div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

      <template v-else>
        <!-- Ask question box -->
        <div class="mb-4">
          <label class="form-label fw-semibold">Ask a question</label>
          <textarea
            class="form-control"
            rows="2"
            v-model="newQuestion"
            placeholder="e.g. What is the condition of this item?"
          />
          <div class="d-flex justify-content-end mt-2">
            <button class="btn btn-primary" :disabled="postingQuestion" @click="submitQuestion">
              {{ postingQuestion ? "Posting..." : "Post question" }}
            </button>
          </div>
          <div v-if="postQuestionError" class="text-danger small mt-2">
            {{ postQuestionError }}
          </div>
        </div>

        <!-- Questions list -->
        <div v-if="questions.length === 0" class="text-muted">
          No questions yet.
        </div>

        <div v-for="q in questions" :key="q.id" class="mb-4">
          <div class="border rounded p-3">
            <div class="d-flex justify-content-between align-items-center">
              <div class="fw-semibold">@{{ q.username }}</div>
              <div class="text-muted small">{{ formatDate(q.createdAt) }}</div>
            </div>

            <div class="mt-2">{{ q.text }}</div>

            <!-- Replies -->
            <div class="mt-3 ps-2 border-start">
              <div v-if="q.replies.length === 0" class="text-muted small">
                No replies yet.
              </div>

              <div v-for="r in q.replies" :key="r.id" class="py-2">
                <div class="d-flex justify-content-between align-items-center">
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-semibold">@{{ r.username }}</span>

                    <!-- owner badge -->
                    <span v-if="r.isOwner" class="badge bg-success">
                      Lister
                    </span>
                  </div>

                  <div class="text-muted small">{{ formatDate(r.createdAt) }}</div>
                </div>

                <div class="mt-1">{{ r.text }}</div>
              </div>

              <!-- Reply box -->
              <div class="mt-3">
                <template v-if="canReply">
                  <input
                    class="form-control"
                    v-model="replyDraft[q.id]"
                    :placeholder="`Reply to @${q.username}...`"
                    @keydown.enter.prevent="submitReply(q.id)"
                  />

                  <div class="d-flex justify-content-end mt-2">
                    <button
                      class="btn btn-outline-primary btn-sm"
                      :disabled="postingReplyId === q.id"
                      @click="submitReply(q.id)"
                    >
                      {{ postingReplyId === q.id ? "Replying..." : "Reply" }}
                    </button>
                  </div>

                  <div v-if="replyError[q.id]" class="text-danger small mt-1">
                    {{ replyError[q.id] }}
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

interface ForumReply {
  id: number;
  text: string;
  username: string;
  createdAt: string;
  isOwner: boolean;
}

interface ForumQuestion {
  id: number;
  text: string;
  username: string;
  createdAt: string;
  replies: ForumReply[];
}

const props = defineProps<{
  itemId: number;
  isAuthenticated: boolean;
}>();

function getCSRF(): string {
  return (
    document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1] || ""
  );
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString();
}

const loading = ref(true);
const error = ref("");

const questions = ref<ForumQuestion[]>([]);

const newQuestion = ref("");
const postingQuestion = ref(false);
const postQuestionError = ref("");

const replyDraft = ref<Record<number, string>>({});
const replyError = ref<Record<number, string>>({});
const postingReplyId = ref<number | null>(null);

const canReply = ref(false);

async function loadForum(): Promise<void> {
  loading.value = true;
  error.value = "";

  try {
    const res = await fetch(`/api/item/${props.itemId}/forum/`, { credentials: "include" });
    if (!res.ok) throw new Error("Failed to load forum.");

    const data = await res.json();
    questions.value = data.questions ?? [];
    canReply.value = !!data.canReply;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

async function submitQuestion(): Promise<void> {
  postQuestionError.value = "";

  if (!props.isAuthenticated) {
    window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
    return;
  }

  const text = newQuestion.value.trim();
  if (!text) {
    postQuestionError.value = "Question cannot be empty.";
    return;
  }

  postingQuestion.value = true;

  try {
    const res = await fetch(`/api/item/${props.itemId}/questions/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "X-CSRFToken": getCSRF(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    const data = await res.json();
    if (!res.ok) {
      postQuestionError.value = data?.error || "Failed to post question.";
      return;
    }

    // add new question to top
    questions.value.unshift(data.question);
    newQuestion.value = "";
  } finally {
    postingQuestion.value = false;
  }
}

async function submitReply(questionId: number): Promise<void> {
  replyError.value[questionId] = "";

  if (!canReply.value) {
    replyError.value[questionId] = "Only the lister can reply to questions.";
    return;
  }

  if (!props.isAuthenticated) {
    window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
    return;
  }

  const text = (replyDraft.value[questionId] || "").trim();
  if (!text) {
    replyError.value[questionId] = "Reply cannot be empty.";
    return;
  }

  postingReplyId.value = questionId;

  try {
    const res = await fetch(`/api/questions/${questionId}/replies/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "X-CSRFToken": getCSRF(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    const data = await res.json();
    if (!res.ok) {
      replyError.value[questionId] = data?.error || "Failed to reply.";
      return;
    }

    const q = questions.value.find((x) => x.id === questionId);
    if (q) q.replies.push(data.reply);

    replyDraft.value[questionId] = "";
  } finally {
    postingReplyId.value = null;
  }
}

onMounted(loadForum);
</script>
