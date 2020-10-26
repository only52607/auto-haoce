<template>
  <div class="home">
    <a-row type="flex" justify="center" align="top" :bordered="false" style="width: 100%;">
      <a-col :xs="24" :sm="20" :md="16" :lg="8" :xl="6" style="margin:10px;">
        <haoce-user-card
          :user="user"
          :setting="setting"
          :loading="loadingUser"
          @update="updateUserSetting"
          @logout="logout"
        />
      </a-col>

      <a-col :xs="24" :sm="20" :md="16" :lg="8" :xl="6" style="margin:10px;">
        <reading-task-card
          :task="task"
          :loading="loadingTask"
          @stop="stopReadingTask"
          @update="updateTask"
          @create="prepareTask"
        />
      </a-col>

      <a-col :xs="24" :sm="20" :md="16" :lg="14" :xl="10" style="margin:10px;">
        <bookcase-card
          ref="bookcase"
          id="bookcase"
          :loadingBooks="loadingBooks"
          @update="updateBooks"
          @create-task="createReadingTask"
        />
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { getCurrentInstance, onMounted, reactive, ref } from "vue";
import HaoceUserCard from "@/components/HaoceUserCard.vue";
import ReadingTaskCard from "@/components/ReadingTaskCard.vue";
import BookcaseCard from "@/components/BookcaseCard.vue";
import bookStore from "@/utils/books.js";
import { message } from "ant-design-vue";
import api from "@/utils/api.js";
import { useRoute, useRouter } from "vue-router";

export default {
  name: "Home",
  components: {
    HaoceUserCard,
    ReadingTaskCard,
    BookcaseCard,
  },
  setup(props, context) {
    const router = useRouter();
    const route = useRoute();
    const { ctx } = getCurrentInstance();
    let loadingTask = ref(false);
    let loadingUser = ref(false);
    let loadingBooks = ref(false);
    let user = ref({
      name: "",
      uid: "",
      user_id: "",
      school: "",
      term: "",
      number: "",
      college_name: "",
      head: "",
    });
    let setting = ref({
      term_id: "",
      term: "",
      user_id: "",
      school_id: "",
      start_time: "",
      end_time: "",
      s_start_time: "",
      s_end_time: "",
      book_limit: "",
      book_limit_min: "",
      end: "",
      is_school_user: "",
      block_id: "",
      class_info: {
        id: "",
        student_cnt: "",
        user_id: "",
        ctime: "",
        task_cnt: "",
        type: "",
        name: "",
      },
    });
    let task = ref({
      is_running: true,
      is_complete: false,
      start_time: 0,
      complete_time: 0,
      current_book_id: 0,
      chapter_list: [],
      current_chapter_index: 0,
      current_chapter_id: 0,
      current_page: 0,
      current_page_count: 0,
    });
    async function updateUserSetting() {
      loadingUser.value = true;
      user.value = (await api.get("/user/info")).data;
      setting.value = (await api.get("/user/setting")).data;
      loadingUser.value = false;
    }
    async function updateTask() {
      loadingTask.value = true;
      task.value = (await api.get("/books/reading_task")).data;
      loadingTask.value = false;
    }
    async function logout() {
      await api.delete("/auth");
      router.replace("/auth");
    }
    async function prepareTask() {
      message.warning("请选择一本书籍及阅读章节后提交任务");
      document.getElementById("bookcase").scrollIntoView(true);
    }
    async function createReadingTask(bookId, chapters) {
      if (task.value.is_running) {
        message.error("已存在一个阅读任务，无法重复提交");
        return;
      }
      try {
        await api.post(`/books/reading_task?book_id=${bookId}`, chapters);
        await updateTask();
        message.success("任务提交成功");
      } catch {
        message.error("任务提交失败");
      }
    }
    async function stopReadingTask() {
      await api.delete("/books/reading_task");
      await updateTask();
      message.warning("任务已被停止");
    }
    async function updateBooks() {
      loadingBooks.value = true;
      try {
        await bookStore.updateBooks();
      } catch {
        message.warning("获取书架失败，请重试");
        // setTimeout(updateBooks, 1000)
      }
      loadingBooks.value = false;
    }
    onMounted(async () => {
      loadingTask.value = true;
      loadingUser.value = true;
      loadingBooks.value = true;
      try {
        await updateUserSetting();
        await updateTask();
      } catch {
        message.warning("请先登录");
        router.replace("/auth");
        return;
      }
      updateBooks();
    });
    return {
      user,
      loadingUser,
      updateUserSetting,
      logout,
      setting,
      task,
      updateTask,
      loadingTask,
      prepareTask,
      createReadingTask,
      stopReadingTask,
      updateBooks,
      loadingBooks,
    };
  },
};
</script>
