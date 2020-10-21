<template>
  <a-card hoverable :title="'我的书架'" :bordered="false" class="book-case-card">
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
            <a-card hoverable @click="onBookSeleted(book.book_id)">
              <template v-slot:cover>
                <img :alt="book.book_info.name" :src="'https://cdn.haoce.com' + book.book_info.img" />
              </template>
              <p class="black single-line">{{book.book_info.name}}</p>
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
        <a-button type="primary" style="margin-bottom:10px" @click="$emit('create-task',selectedBookId,selectedChapterIds)" >
           提交阅读任务
        </a-button>
      <a-checkbox-group v-model:value="selectedChapterIds">
        <a-row>
            <a-col :span="24" v-for="chapter in selectedBookData.chapters" :key="chapter.cp_id">
                <a-checkbox :value="chapter.cp_id" :key="chapter.cp_id" >{{chapter.chapter}}</a-checkbox>
            </a-col>
        </a-row>
      </a-checkbox-group>
       
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
} from "vue";
import bookStore from "@/utils/books.js";

export default {
  props: [],
  setup() {
    const { ctx } = getCurrentInstance();
    let selectedBookId = ref(0);
    let selectedBookName = computed(() => {
      if (!bookStore.books.value[selectedBookId.value]) return "";
      return bookStore.books.value[selectedBookId.value].book_info.name;
    });
    let selectedChapterIds = []
    let books = computed(() => {
      let _books = [];
      for (let key in bookStore.books.value) {
        _books.push(bookStore.books.value[key]);
      }
      return _books;
    });
    let bookDetailVisible = ref(false);
    let selectedBookData = ref({})
    async function onBookSeleted(bookId) {
      //selectedChapterIds.splice(0)
      selectedBookId.value = bookId;
      bookDetailVisible.value = true;
      await bookStore.updateBookData(selectedBookId.value)
      let bookData = bookStore.bookDatas[selectedBookId.value]
      if (!bookData) selectedBookData.value = {"chapters":{}}
      else selectedBookData.value = bookData
    }
    
    // let selectedBookData = computed(async ()=>{
    //     let bookData = bookStore.bookDatas[selectedBookId.value]
    //     if (!bookData) return {"chapters":{}}
    //     return bookData
    // })
    return {
      books,
      onBookSeleted,
      bookDetailVisible,
      selectedBookId,
      selectedBookName,
      selectedChapterIds,
      selectedBookData
    };
  },
};
</script>

<style>
.book-case-card {
  overflow: hidden;
}
.single-line {
  font-size: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.black {
  color: #2c3e50;
}
</style>
