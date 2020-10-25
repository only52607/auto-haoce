<template>
  <a-card hoverable :title="'自动阅读'" class="haoce-user-card" :bordered="false">
    <a-spin v-if="loading" />
    <template v-if="task.start_time == 0">
      <a-empty
        image="https://gw.alipayobjects.com/mdn/miniapp_social/afts/img/A*pevERLJC9v0AAAAAAAAAAABjAQAAAQ/original"
        :image-style="{
          height: '60px',
        }"
      >
        <template v-slot:description>
          <span>你最近没有创建阅读任务噢</span>
        </template>
        <a-button type="primary" @click="$emit('create')">创建任务</a-button>
      </a-empty>
    </template>

    <template v-else>
      <template v-if="task.is_complete">
        <a-result
          status="success"
          title="阅读任务已完成！"
          :sub-title="`阅读书籍：${bookName}\n共完成章节：${task.chapter_list.length}\n阅读时长：${formatSeconds(task.complete_time - task.start_time)}`"
        >
          <template #extra>
            <a-button type="primary" @click="$emit('create')">创建新任务</a-button>
          </template>
        </a-result>
      </template>
      <template v-else-if="!task.is_running">
        <a-result
          status="warning"
          title="任务已被终止"
          :sub-title="`阅读书籍：${bookName}`"
        >
          <template #extra>
            <a-button type="primary" @click="$emit('create')">创建新任务</a-button>
          </template>
        </a-result>
      </template>
      <template v-else-if="task.is_running">
        <p>
          <icon-font type="icon-book" />
          正在阅读： {{bookName}}
          <a-button type="danger" size="small" @click="$emit('stop')" ghost>停止</a-button>
        </p>
        <a-row :gutter="0" justify="space-around" align="middle" style="margin-bottom:10px">
          <a-col :span="12">
            <a-statistic title="阅读章节" :value="task.current_chapter_index + 1">
              <template #suffix>
                <span>/ {{task.chapter_list.length}}</span>
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="12">
            <a-statistic-countdown title="已阅读时长" :value="2 * nowTime - task.start_time * 1000" />
          </a-col>
        </a-row>
      </template>
      <a-collapse :bordered="false">
        <a-collapse-panel
          key="1"
          header="阅读进度详情"
          :style="'background: #f7f7f7;border-radius: 4px;margin-bottom: 24px;border: 0;overflow: hidden'"
        >
          <a-steps
            progress-dot
            :current="task.current_chapter_index"
            :status="currentStatus"
            direction="vertical"
            size="small"
          >
            <a-step
              v-for="chapter in selectedChapters"
              :key="chapter.cp_id"
              :title="chapter.chapter"
              :description="chapter.description"
            />
          </a-steps>
        </a-collapse-panel>
      </a-collapse>
    </template>

    <template #extra>
      <a-button :loading="loading" @click="$emit('update')" type="dashed">
        <redo-outlined #icon />
      </a-button>
    </template>
  </a-card>
</template>

<script>
import {
  getCurrentInstance,
  reactive,
  ref,
  computed,
  watch,
  watchEffect,
  onMounted,
} from "vue";
import { RedoOutlined } from "@ant-design/icons-vue";
import bookStore from "@/utils/books.js";
import timeFormater from "@/utils/timeFormater.js";

let selectedChapters = ref([]);

export default {
  components: { RedoOutlined },
  props: ["task", "loading"],
  setup(props,context) {
    const { ctx } = getCurrentInstance();
    let bookName = computed(() => {
      let book = bookStore.books.value[props.task.current_book_id];
      if (!book) return "";
      return book.book_info.name;
    });
    let currentStatus = computed(() => {
      if (props.task.is_complete) return "finish";
      if (props.task.is_running) return "process";
      else return "error";
    });
    let nowTime = ref(0);
    onMounted(async () => {
      nowTime.value = Date.now();
      setInterval(() => (nowTime.value += 1000), 1000);
    });
    return {
      bookName,
      currentStatus,
      nowTime,
      formatSeconds: timeFormater.formatSeconds,
      selectedChapters,
    };
  },
  watch: {
    //只能放在watch里生效，奇怪的bug
    async task(value) {
      await bookStore.updateBookData(value.current_book_id);
      let bookData = bookStore.bookDatas[this.task.current_book_id];
      if (!bookData) return [];
      let chapters = {};
      bookData.chapters.forEach((element) => {
        chapters[element.cp_id] = element;
      });
      let _currentChapters = [];
      this.task.chapter_list.forEach((element, index) => {
        let pushedElement = chapters[element];
        if (index < this.task.current_chapter_index)
          pushedElement.description = "阅读完毕";
        else if (index > this.task.current_chapter_index)
          pushedElement.description = "等待阅读";
        else
          pushedElement.description = `正在阅读：${this.task.current_page + 1}/${this.task.current_page_count - 1}`;
        _currentChapters.push(pushedElement);
      });
      selectedChapters.value = _currentChapters;
    },
  },
};
</script>

<style>
</style>