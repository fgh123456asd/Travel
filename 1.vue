<template>
  <div class="fixed-background-layer"></div>

  <Header></Header>
  <div class="main">
    <div class="content-wrapper">
      <div class="header-section">
        <h1 class="main-title">30秒生成你的智能旅行计划</h1>
        <p class="sub-title">覆盖山东 16 地市 · 200+ 景点资源 · AI 一键生成完整行程</p>
      </div>

      <div class="form-card">
        <div class="card-title">
          <span class="sparkle-icon">✨</span> 快速填写旅行需求
        </div>

        <div class="form-content">
          <div class="form-row row-four-cols">
            <div class="form-item">
              <label>出发地</label>
              <div class="input-wrapper">
                <span class="icon">📍</span>
                <input v-model="form.departure" type="text" placeholder="选择出发地" />
              </div>
            </div>
            <div class="form-item">
              <label class="required">目的地</label>
              <div class="input-wrapper">
                <span class="icon">🛫</span>
                <input v-model="form.destination" type="text" placeholder="选择目的地" />
              </div>
            </div>
            <div class="form-item">
              <label>出行日期</label>
              <div class="input-wrapper">
                <span class="icon">📅</span>
                <input v-model="form.date" type="date" placeholder="选择日期" />
              </div>
            </div>
            <div class="form-item">
              <label>旅行天数</label>
              <div class="select-wrapper">
                <span class="icon">📅</span>
                <select v-model="form.days">
                  <option value="" disabled selected hidden>选择天数</option>
                  <option value="1">1天</option>
                  <option value="2">2天</option>
                  <option value="3">3天</option>
                  <option value="4">4天</option>
                  <option value="5">5天</option>
                  <option value="6">6天及以上</option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-row row-two-cols">
            <div class="form-item">
              <label>同行人数</label>
              <div class="select-wrapper">
                <span class="icon">👥</span>
                <select v-model="form.companions">
                  <option value="" disabled selected hidden>选择同行人数</option>
                  <option value="1">1 人 (独自旅行)</option>
                  <option value="2">2 人 (情侣/朋友)</option>
                  <option value="3-5">3-5 人 (家庭/结伴)</option>
                  <option value="6+">6人以上 团队</option>
                </select>
              </div>
            </div>
            <div class="form-item">
              <label>预算范围 <span>(可选)</span></label>
              <div class="input-wrapper">
                <span class="icon">💰</span>
                <input v-model="form.budget" type="text" placeholder="如：3000-5000元" />
              </div>
            </div>
          </div>

          <div class="form-item preference-item">
            <label>兴趣偏好 <span>(可选)</span></label>
            <div class="tags-container">
              <transition-group name="tag-fade">
                <button
                  v-for="tag in displayedTags"
                  :key="tag.name"
                  class="tag-btn"
                  :class="{ active: form.selectedTags.includes(tag.name) }"
                  @click="toggleTag(tag.name)"
                >
                  {{ tag.icon }} {{ tag.name }}
                </button>
              </transition-group>

              <button class="tag-btn more-btn" @click="isExpanded = !isExpanded">
                {{ isExpanded ? '× 收起' : '··· 更多' }}
              </button>
            </div>
          </div>

          <div class="form-footer">
            <div class="footer-tips">
              填写目的地后点击生成，AI 为您量身定制专属行程
            </div>
            <button class="generate-btn" :disabled="isGenerating || isChatting" @click="handleGenerate">
              <span v-if="isGenerating" class="loading-spinner">⏳</span>
              <span v-else>✨</span>
              {{ isGenerating ? 'AI 正在全力规划中...' : '免费生成行程' }}
            </button>
          </div>
        </div>
      </div>

      <transition name="result-fade">
        <div v-if="isGenerating || generatedRawMarkdown" class="result-card">
          <div class="result-header">
            <div class="title-left">
              <span class="ai-badge">AI 智能方案</span>
              <h3>为您定制的专属旅行计划</h3>
            </div>
            <button v-if="generatedRawMarkdown && !isGenerating && !isChatting" class="share-btn" @click="copyTrip">📋 复制计划文本</button>
          </div>

          <div v-if="isGenerating && !generatedRawMarkdown" class="loading-box">
            <div class="pulse-loader"></div>
            <p>AI 正在唤醒中，请稍候...</p>
          </div>

          <div v-else class="result-content markdown-body">
            <div v-html="renderedHtml"></div>
            <span v-if="isGenerating || isChatting" class="typing-cursor">|</span>
          </div>

          <div v-if="generatedRawMarkdown && !isGenerating" class="follow-up-section">
            <div class="follow-up-title">💬 对已有行程不满意？告诉 AI 帮你修改（如：“把第2天换成去青岛海岸”、“预算降到800”）：</div>
            <div class="chat-input-wrapper">
              <input
                v-model="followUpQuery"
                type="text"
                placeholder="在此输入您的修改意见或追加问题..."
                :disabled="isChatting"
                @keyup.enter="handleFollowUpSubmit"
              />
              <button class="send-btn" :disabled="isChatting || !followUpQuery.trim()" @click="handleFollowUpSubmit">
                <span v-if="isChatting">⏳ 规划中</span>
                <span v-else>🚀 发送</span>
              </button>
            </div>
          </div>

          <div ref="resultAnchor" style="height: 1px;"></div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from "vue";
import { marked } from "marked";
import Header from "@/components/home/Header.vue";
import { useRouter } from 'vue-router'
// ⭐ 引入引入用户 Store 模块
import { useUserStore } from "@/stores/user.js";
// ⭐ 引入流式接口函数
import { agentPrint, agentChat } from "@/network/agent.js";

const router = useRouter()
const userStore = useUserStore() // ⭐ 实例化 Store

const allTags = [
  { name: '自然风光', icon: '🏔️' },
  { name: '历史文化', icon: '🏛️' },
  { name: '美食体验', icon: '🍜' },
  { name: '亲子研学', icon: '👨‍👩‍👦' },
  { name: '海滨度假', icon: '🌊' },
  { name: '网红打卡', icon: '📸' },
  { name: '户外运动', icon: '🚴' },
  { name: '购物狂欢', icon: '🛍️' },
  { name: '艺术展览', icon: '🎨' },
  { name: '休闲养生', icon: '💆' },
];

const isExpanded = ref(false);
const isGenerating = ref(false);
const generatedRawMarkdown = ref("");
const resultAnchor = ref(null);

const followUpQuery = ref("");
const isChatting = ref(false);
const currentThreadId = ref("");

const form = reactive({
  departure: '',
  destination: '',
  date: '',
  days: '',
  companions: '',
  budget: '',
  selectedTags: []
});

const renderedHtml = computed(() => {
  if (!generatedRawMarkdown.value) return "";
  return marked.parse(generatedRawMarkdown.value);
});

const displayedTags = computed(() => {
  return isExpanded.value ? allTags : allTags.slice(0, 5);
});

const toggleTag = (tagName) => {
  const index = form.selectedTags.indexOf(tagName);
  if (index > -1) {
    form.selectedTags.splice(index, 1);
  } else {
    form.selectedTags.push(tagName);
  }
};

const getCompanionText = (val) => {
  if (!val) return '未选择';
  const dict = {
    '1': '1 人 (独自旅行)',
    '2': '2 人 (情侣/朋友)',
    '3-5': '3-5 人 (家庭/结伴)',
    '6+': '6人以上 团队'
  };
  return dict[val] || `${val}人`;
};

const scrollToBottom = (isSmooth = false) => {
  if (!resultAnchor.value) return;

  const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;
  const clientHeight = document.documentElement.clientHeight || document.body.clientHeight;
  const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;

  if (scrollHeight - scrollTop - clientHeight < 600) {
    window.scrollTo({
      top: scrollHeight,
      behavior: isSmooth ? 'smooth' : 'auto'
    });
  }
};

/**
 * ⭐ 改造后的 handleGenerate：使用当前登录的用户 ID 作为唯一 thread_id 标识
 */
const handleGenerate = async () => {
  // 1. 安全拦截：校验 Pinia 登录状态
  if (!userStore.isLoggedIn || !userStore.userInfo?.id) {
    alert('请先登录后再进行 AI 旅行规划！');
    router.push('/login');
    return;
  }

  if (!form.destination.trim()) {
    alert('请先填写目的地！');
    return;
  }

  isGenerating.value = true;
  generatedRawMarkdown.value = "";

  // 2. 核心更改：将 thread_id 修改为绑定的用户 id
  currentThreadId.value = `user_${userStore.userInfo.id}`;

  nextTick(() => {
    resultAnchor.value?.scrollIntoView({ behavior: 'smooth' });
  });

  const payload = {
    thread_id: currentThreadId.value,
    form_data: {
      departure: form.departure || '未填写',
      destination: form.destination,
      start_date: form.date || '未选择',
      days: form.days ? `${form.days}天` : '未选择',
      travelers: getCompanionText(form.companions),
      budget: form.budget || '未填写',
      preferences: [...form.selectedTags]
    }
  };

  try {
    // 🚀 流式生成调用
    await agentPrint(payload, (chunk) => {
      generatedRawMarkdown.value += chunk;
      nextTick(() => {
        scrollToBottom(false);
      });
    });

    nextTick(() => {
      scrollToBottom(true);
    });

  } catch (error) {
    console.error("流式读取失败:", error);
    alert("行程规划失败，请稍后重试。");
  } finally {
    isGenerating.value = false;
  }
};

/**
 * ⭐ 改造后的 handleFollowUpSubmit：自动复用用户 ID 会话进行多轮对话
 */
const handleFollowUpSubmit = async () => {
  const queryText = followUpQuery.value.trim();
  if (!queryText || isChatting.value) return;

  if (!currentThreadId.value) {
    alert("会话 ID 丢失，请重新填写表单生成初始行程！");
    return;
  }

  isChatting.value = true;
  followUpQuery.value = "";
  generatedRawMarkdown.value += `\n\n---\n\n> 🙋‍♂️ **我的修改意见：** ${queryText}\n\n`;

  nextTick(() => {
    scrollToBottom(true);
  });

  const payload = {
    thread_id: currentThreadId.value,
    message: queryText
  };

  try {
    // 🚀 多轮调优调用
    await agentChat(payload, (chunk) => {
      generatedRawMarkdown.value += chunk;
      nextTick(() => {
        scrollToBottom(false);
      });
    });

  } catch (error) {
    console.error("多轮对话流读取出错:", error);
    generatedRawMarkdown.value += `\n\n❌ *系统提示：AI 调整行程失败，请检查 network 或稍后重试。*`;
  } finally {
    isChatting.value = false;
    nextTick(() => {
      scrollToBottom(true);
    });
  }
};

const copyTrip = () => {
  navigator.clipboard.writeText(generatedRawMarkdown.value);
  alert('🚀 行程方案已成功复制到剪贴板！');
};
</script>

<style lang="less" scoped>
/* 🎯 🔥 彻底锁死、固定背景图，不随内容而动 */
.fixed-background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("@/assets/images/agent.png");
  background-size: cover;
  background-position: center top;
  background-repeat: no-repeat;
  z-index: -1;

  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
  pointer-events: none;
  will-change: transform;
}

.main {
  padding-top: 70px;
  width: 100%;
  min-height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-x: hidden;

  .content-wrapper {
    width: 100%;
    max-width: 1000px;
    padding: 0 20px 60px;
    box-sizing: border-box;

    .header-section {
      margin-top: 40px;
      text-align: center;
      margin-bottom: 32px;

      .main-title {
        font-weight: 700;
        font-size: 45px;
        color: #2f856c;
        margin: 0 0 12px;
        letter-spacing: 2px;
      }

      .sub-title {
        font-size: 16px;
        color: #555;
        margin: 0;
        letter-spacing: 1px;
      }
    }

    .form-card {
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      padding: 30px;
      box-shadow: 0 12px 32px rgba(47, 133, 108, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.6);

      .card-title {
        font-size: 18px;
        font-weight: 700;
        color: #1e3a31;
        margin-bottom: 24px;
        display: flex;
        align-items: center;

        .sparkle-icon {
          color: #2f856c;
          margin-right: 8px;
        }
      }

      .form-content {
        display: flex;
        flex-direction: column;
        gap: 20px;

        .form-row {
          display: flex;
          gap: 16px;
          width: 100%;
          flex-wrap: wrap;

          &.row-four-cols .form-item {
            flex: 1;
            min-width: 180px;
          }

          &.row-two-cols .form-item {
            flex: 1;
            min-width: 280px;
          }
        }

        .form-item {
          display: flex;
          flex-direction: column;
          gap: 8px;

          label {
            font-size: 14px;
            color: #4a5553;
            font-weight: 500;

            &.required::after {
              content: ' *';
              color: #ff4d4f;
            }

            span {
              font-size: 12px;
              color: #999;
              font-weight: normal;
            }
          }

          .input-wrapper, .select-wrapper {
            position: relative;
            display: flex;
            align-items: center;

            .icon {
              position: absolute;
              left: 12px;
              font-size: 14px;
              color: #8a9995;
              pointer-events: none;
            }

            input, select {
              width: 100%;
              height: 44px;
              padding: 0 12px 0 36px;
              border: 1px solid #e1e8e6;
              border-radius: 8px;
              background-color: #fff;
              font-size: 14px;
              color: #333;
              outline: none;
              transition: all 0.3s ease;
              box-sizing: border-box;

              &:focus {
                border-color: #2f856c;
                box-shadow: 0 0 0 2px rgba(47, 133, 108, 0.1);
              }

              &::placeholder {
                color: #b0beb8;
              }
            }

            select {
              appearance: none;
              cursor: pointer;
              background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238a9995' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
              background-repeat: no-repeat;
              background-position: right 12px center;
              padding-right: 32px;
            }
          }
        }

        .preference-item {
          margin-top: 8px;

          .tags-container {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;

            .tag-btn {
              display: flex;
              align-items: center;
              padding: 8px 16px;
              background: #f4f7f6;
              border: 1px solid #e1e8e6;
              border-radius: 20px;
              font-size: 14px;
              color: #4a5553;
              cursor: pointer;
              transition: all 0.2s ease;
              user-select: none;

              &:hover {
                background: #e9f0ee;
                border-color: #2f856c;
                color: #2f856c;
              }

              &.active {
                background: #e6f3f0;
                border-color: #2f856c;
                color: #2f856c;
                font-weight: 500;
              }

              &.more-btn {
                background: transparent;
                border: 1px solid #e1e8e6;
                color: #2f856c;
                font-weight: bold;

                &:hover {
                  background: #f0fdfa;
                }
              }
            }
          }
        }

        .form-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 15px;
          border-top: 1px solid rgba(225, 232, 230, 0.5);
          padding-top: 20px;
          flex-wrap: wrap;
          gap: 16px;

          .footer-tips {
            font-size: 14px;
            color: #8a9995;
          }

          .generate-btn {
            background-color: #218367;
            color: white;
            border: none;
            padding: 12px 28px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 4px 12px rgba(33, 131, 103, 0.3);
            transition: all 0.2s ease;

            &:disabled {
              background-color: #a3c4ba;
              cursor: not-allowed;
              box-shadow: none;
            }

            &:hover:not(:disabled) {
              background-color: #1a6b54;
              transform: translateY(-1px);
              box-shadow: 0 6px 16px rgba(33, 131, 103, 0.4);
            }
          }
        }
      }
    }

    .result-card {
      margin-top: 30px;
      background: rgba(255, 255, 255, 0.98);
      backdrop-filter: blur(15px);
      border-radius: 20px;
      padding: 35px;
      box-shadow: 0 20px 40px rgba(33, 131, 103, 0.06);
      border: 1px solid rgba(47, 133, 108, 0.15);

      .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px dashed #e1e8e6;
        padding-bottom: 20px;
        margin-bottom: 24px;
        flex-wrap: wrap;
        gap: 12px;

        .title-left {
          display: flex;
          align-items: center;
          gap: 12px;

          .ai-badge {
            font-size: 12px;
            background: linear-gradient(135deg, #2f856c 0%, #155e48 100%);
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
          }

          h3 {
            font-size: 20px;
            color: #1e3a31;
            margin: 0;
            font-weight: 700;
          }
        }

        .share-btn {
          background: none;
          border: 1px solid #2f856c;
          color: #2f856c;
          padding: 6px 14px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;

          &:hover {
            background: #e6f3f0;
          }
        }
      }

      .loading-box {
        text-align: center;
        padding: 40px 0;
        color: #68827a;

        .pulse-loader {
          width: 40px;
          height: 40px;
          background-color: #2f856c;
          border-radius: 50%;
          margin: 0 auto 16px;
          animation: pulse 1.2s infinite ease-in-out;
        }
      }

      .markdown-body {
        font-size: 15px;
        color: #333;
        line-height: 1.8;
        background: #fdfdfd;
        border: 1px solid #f0f4f2;
        padding: 30px;
        border-radius: 12px;
        word-break: break-all;
        position: relative;

        .typing-cursor {
          display: inline-block;
          width: 2px;
          font-weight: bold;
          color: #2f856c;
          margin-left: 4px;
          animation: blink 0.8s infinite;
        }

        :deep(h1) {
          font-size: 24px;
          color: #1a6b54;
          margin-top: 20px;
          margin-bottom: 16px;
          border-bottom: 2px solid #e1e8e6;
          padding-bottom: 8px;
        }

        :deep(h2) {
          font-size: 19px;
          color: #2f856c;
          margin-top: 28px;
          margin-bottom: 14px;
          padding-left: 8px;
          border-left: 4px solid #2f856c;
        }

        :deep(h3) {
          font-size: 16px;
          color: #34495e;
          margin-top: 20px;
          margin-bottom: 10px;
          font-weight: 600;
        }

        :deep(p) { margin: 0 0 12px; }
        :deep(strong) { color: #1a6b54; }

        :deep(hr) {
          border: none;
          border-top: 1px dashed #c3dad2;
          margin: 28px 0;
        }

        :deep(ul), :deep(ol) {
          padding-left: 20px;
          margin-bottom: 16px;
          li { margin-bottom: 6px; }
        }

        :deep(table) {
          width: 100%;
          border-collapse: collapse;
          margin: 20px 0;
          font-size: 14px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.02);

          th, td {
            border: 1px solid #e1e8e6;
            padding: 12px 16px;
            text-align: left;
          }

          th {
            background-color: #edf4f2;
            color: #1e3a31;
            font-weight: 600;
            white-space: nowrap;
          }

          tr:nth-child(even) { background-color: #fafcfb; }
        }

        :deep(blockquote) {
          margin: 16px 0;
          padding: 12px 20px;
          background-color: #f0fdfa;
          border-left: 4px solid #218367;
          color: #1a6b54;
          border-radius: 0 8px 8px 0;
          p { margin: 0; }
        }
      }

      .follow-up-section {
        margin-top: 30px;
        border-top: 2px dashed #e1e8e6;
        padding-top: 20px;

        .follow-up-title {
          font-size: 14px;
          color: #4a5553;
          font-weight: 500;
          margin-bottom: 12px;
        }

        .chat-input-wrapper {
          display: flex;
          gap: 12px;
          align-items: center;

          input {
            flex: 1;
            height: 46px;
            padding: 0 16px;
            border: 1px solid #c3dad2;
            border-radius: 24px;
            background-color: #fff;
            font-size: 14px;
            color: #333;
            outline: none;
            transition: all 0.3s ease;
            box-shadow: inset 0 1px 4px rgba(0, 0, 0, 0.02);

            &:focus {
              border-color: #2f856c;
              box-shadow: 0 0 0 3px rgba(47, 133, 108, 0.15);
            }

            &:disabled {
              background-color: #f5f7f6;
              cursor: not-allowed;
            }
          }

          .send-btn {
            height: 46px;
            padding: 0 24px;
            background: linear-gradient(135deg, #2f856c 0%, #1a6b54 100%);
            color: white;
            border: none;
            border-radius: 24px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 10px rgba(47, 133, 108, 0.2);
            white-space: nowrap;

            &:disabled {
              background: #cbd5e1;
              color: #94a3b8;
              cursor: not-allowed;
              box-shadow: none;
            }

            &:hover:not(:disabled) {
              transform: translateY(-1px);
              box-shadow: 0 6px 14px rgba(47, 133, 108, 0.3);
            }
          }
        }
      }
    }
  }
}

.tag-fade-enter-active, .tag-fade-leave-active { transition: all 0.25s ease; }
.tag-fade-enter-from, .tag-fade-leave-to { opacity: 0; transform: translateY(8px); }

.result-fade-enter-active { transition: all 0.5s ease-out; }
.result-fade-enter-from { opacity: 0; transform: translateY(30px); }

@keyframes pulse {
  0% { transform: scale(0); opacity: 0.8; }
  100% { transform: scale(1.2); opacity: 0; }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@media (max-width: 768px) {
  .main .content-wrapper {
    .header-section {
      .main-title { font-size: 30px; }
      .sub-title { font-size: 14px; }
    }
    .form-card {
      padding: 20px;
      .form-content .form-footer {
        flex-direction: column;
        align-items: stretch;
        text-align: center;
        .generate-btn { justify-content: center; }
      }
    }
    .result-card {
      padding: 20px;
      .result-header {
        flex-direction: column;
        align-items: flex-start;
        .share-btn { width: 100%; text-align: center; }
      }
      .markdown-body {
        padding: 15px;
        overflow-x: auto;
      }
    }
  }
}
</style>