<template>
  <a-card hoverable :title="'自动阅读'" class="haoce-user-card" :bordered="false">
    <template v-if="task.start_time == 0">
      <a-empty
        image="https://gw.alipayobjects.com/mdn/miniapp_social/afts/img/A*pevERLJC9v0AAAAAAAAAAABjAQAAAQ/original"
        :image-style="{
          height: '60px',
        }"
      >
        <template v-slot:description>
          <span>你还没有创建过阅读任务噢</span>
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
        <a-result status="warning" title="任务已被终止">
          <template #extra>
            <a-button type="primary" @click="$emit('create')">创建新任务</a-button>
          </template>
        </a-result>
      </template>
      <template v-else-if="task.is_running">
        <p>
          <icon-font type="icon-book" />
          正在阅读： {{bookName}}
          <a-button type="danger" size="small" ghost>停止</a-button>
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
            <template v-for="chapter in currentChapters">
              <a-step :title="chapter.chapter" :description="chapter.description" />
            </template>
          </a-steps>
        </a-collapse-panel>
      </a-collapse>
    </template>

    <template #extra>
      <a-button @click="$emit('update')">更新</a-button>
      <!-- <a-button type="danger" v-if="showCancel" @click="$emit('stop')">结束任务</a-button>
      <template v-else>
        <a-button type="primary" v-if="!showEmpty" @click="$emit('create')">创建新任务</a-button>
      </template>-->
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
import bookStore from "@/utils/books.js";

export default {
  components: {},
  props: ["task"],
  setup() {
    const { ctx } = getCurrentInstance();
    let bookName = computed(() => {
      return bookStore.books.value[ctx.task.current_book_id].book_info.name;
    });
    let currentChapters = computed(() => {
      let bookData = bookStore.bookDatas[ctx.task.current_book_id];
      let chapters = {};
      bookData.chapters.forEach((element) => {
        chapters[element.cp_id] = element;
      });
      let _currentChapters = [];
      ctx.task.chapter_list.forEach((element, index) => {
        let pushedElement = chapters[element];
        if (index < ctx.task.current_chapter_index)
          pushedElement.description = "阅读完毕";
        else if (index > ctx.task.current_chapter_index)
          pushedElement.description = "等待阅读";
        else
          pushedElement.description = `正在阅读：${ctx.task.current_page}/${ctx.task.current_page_count}`;
        _currentChapters.push(pushedElement);
      });
      return _currentChapters;
    });
    let currentStatus = computed(() => {
      if (ctx.task.is_complete) return "finish";
      if (ctx.task.is_running) return "process";
      else return "error";
    });
    let nowTime = ref(0);
    function formatSeconds(value) {
      let theTime = parseInt(value);
      let middle = 0;
      let hour = 0;
      if (theTime > 60) {
        middle = parseInt(theTime / 60);
        theTime = parseInt(theTime % 60);
        if (middle > 60) {
          hour = parseInt(middle / 60);
          middle = parseInt(middle % 60);
        }
      }
      let result = "" + parseInt(theTime) + "秒";
      if (middle > 0) {
        result = "" + parseInt(middle) + "分" + result;
      }
      if (hour > 0) {
        result = "" + parseInt(hour) + "时" + result;
      }
      return result;
    }
    onMounted(() => {
      nowTime.value = Date.now();
      setInterval(() => (nowTime.value += 1000), 1000);
    });
    return {
      bookName,
      currentChapters,
      currentStatus,
      nowTime,
      formatSeconds
    };
  },
};
</script>

<style>
</style>