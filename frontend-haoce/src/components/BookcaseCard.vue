<template>
  <a-card hoverable :title="'我的书架'" :bordered="false" class="book-case-card">
    <template #extra>
      <a-button :loading="loadingBooks" @click="$emit('update')" type="dashed">
        <redo-outlined #icon />
      </a-button>
    </template>
    <a-spin v-if="loadingBooks" />
    <a-row
      type="flex"
      justify="center"
      align="top"
      :bordered="false"
      style="width: 100%;height: 100%"
    >
      <template v-for="book in books">
        <a-col :xs="6" :sm="6" :md="6" :lg="6" :xl="6" style="margin:0px;">
          <a-tooltip placement="topLeft" :title="book.book_info.name">
            <a-card
              hoverable
              @click="onBookSeleted(book.book_id)"
              size="small"
              style="overflow: hidden;"
            >
              <template v-slot:cover>
                <img :alt="book.book_info.name" :src="'https://cdn.haoce.com' + book.book_info.img" />
              </template>
              <p class="black loop single-line">{{book.book_info.name}}</p>
              <p class="single-line">{{book.book_info.writer}}</p>
            </a-card>
          </a-tooltip>
        </a-col>
      </template>
    </a-row>
    <a-drawer
      :title="selectedBookName"
      placement="bottom"
      :closable="true"
      :visible="bookDetailVisible"
      :get-container="false"
      :wrap-style="{ position: 'absolute', }"
      height="90%"
      @close="bookDetailVisible=false"
    >
      <p>
        <icon-font type="icon-class" />
        教学班： {{selectedBookClass}}
      </p>
      <p>已阅读：{{selectedBookData.view_data.progress/100}}% 用时： {{formatSeconds(selectedBookData.view_data.dtime)}}</p>
      <a-button
        type="primary"
        style="margin-bottom:10px;"
        @click="bookDetailVisible=false;$emit('create-task',selectedBookId,selectedChapterIds,pageCount,pageDelay)"
      >提交阅读任务</a-button>
      <div style="margin-bottom:10px;">
        每章节页数：<a-input-number v-model:value="pageCount" :min="2" :max="50" />
        每页阅读时间（秒）：<a-input-number v-model:value="pageDelay" :min="20" :max="600" />
      </div>
      

      <a-spin v-if="loadingChapters" />
      <template v-else>
        <a-checkbox-group v-model:value="selectedChapterIds">
          <a-row>
            <a-col :span="24" v-for="chapter in selectedBookData.chapters" :key="chapter.cp_id">
              <a-checkbox
                :value="chapter.cp_id"
                :key="chapter.cp_id"
              >{{chapter.chapter + "(" + getChapterReadInfo(chapter.cp_id) + ")"}}</a-checkbox>
            </a-col>
          </a-row>
        </a-checkbox-group>
      </template>
    </a-drawer>
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
import timeFormater from "@/utils/timeFormater.js";
import { RedoOutlined } from "@ant-design/icons-vue";

export default {
  components: { RedoOutlined },
  data() {
    return {
      selectedChapterIds: [], //不放在data里选择框会无法点击
    };
  },
  props: ["loadingBooks"],
  setup() {
    let loadingChapters = ref(false);
    let selectedBookId = ref(0);
    let selectedBookName = computed(() => {
      if (!bookStore.books.value[selectedBookId.value]) return "";
      return bookStore.books.value[selectedBookId.value].book_info.name;
    });
    let selectedBookClass = computed(() => {
      if (!bookStore.books.value[selectedBookId.value]) return "";
      return bookStore.books.value[selectedBookId.value].class_info.name;
    });
    let pageCount  = ref(20)
    let pageDelay = ref(90)
    let books = computed(() => {
      let _books = [];
      for (let key in bookStore.books.value) {
        _books.push(bookStore.books.value[key]);
      }
      return _books;
    });
    let bookDetailVisible = ref(false);
    let selectedBookData = ref({
      chapters: [],
      view_data: {},
      chapters_view_data: {},
    });
    async function onBookSeleted(bookId) {
      selectedBookId.value = bookId;
      bookDetailVisible.value = true;
      loadingChapters.value = true;
      await bookStore.updateBookData(selectedBookId.value);
      let bookData = bookStore.bookDatas[selectedBookId.value];
      if (bookData) selectedBookData.value = bookData;
      loadingChapters.value = false;
    }
    function getChapterReadInfo(chapterId) {
      let info = selectedBookData.value.chapters_view_data[chapterId];
      if (!info) return "未阅读";
      return `已阅读：${
        info.progress / 100
      }% 用时：${timeFormater.formatSeconds(info.dtime)}`;
    }
    function sleep(time) {
      return new Promise((resolve) => setTimeout(resolve, time));
    }
    return {
      books,
      onBookSeleted,
      bookDetailVisible,
      selectedBookId,
      selectedBookName,
      selectedBookData,
      selectedBookClass,
      formatSeconds: timeFormater.formatSeconds,
      getChapterReadInfo,
      loadingChapters,
      pageCount,
      pageDelay
    };
  },
};
</script>

<style>
.book-case-card {
  overflow: hidden;
}
/* text-overflow: ellipsis; */
.single-line {
  font-size: 5px;
  line-height: 12px;
  overflow: hidden;
  text-overflow:ellipsis;
  white-space: nowrap;
}
.loop {
  display: inline-block;
  animation: 20s wordsLoop linear infinite normal;
}
.black {
  color: #2c3e50;
}
@keyframes wordsLoop {
  0% {
    transform: translateX(0px);
    -webkit-transform: translateX(0px);
  }
  100% {
    transform: translateX(-50%);
    -webkit-transform: translateX(-50%);
  }
}

@-webkit-keyframes wordsLoop {
  0% {
    transform: translateX(0px);
    -webkit-transform: translateX(0px);
  }
  100% {
    transform: translateX(-50%);
    -webkit-transform: translateX(-50%);
  }
}
</style>
