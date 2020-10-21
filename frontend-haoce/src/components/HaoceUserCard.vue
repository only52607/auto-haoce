<template>
  <a-card hoverable :title="'我的好策'" class="haoce-user-card" :bordered="false">
    <p><icon-font type="icon-user" /> 姓名： {{user.name}}</p>
    <p><icon-font type="icon-number" /> 学号： {{user.number}}</p>
    <p><icon-font type="icon-school" /> 学校： {{user.school}}</p>
    <p><icon-font type="icon-college" /> 学院： {{user.college_name}}</p>
    <p><icon-font type="icon-date" /> 当前学期： {{setting.term}}</p>
    <p><icon-font type="icon-class" /> 当前教学班： {{setting.class_info.name}}（共{{setting.class_info.student_cnt}}人）</p>
    <template #extra>
        <a-avatar :src="user.head" />
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
} from "vue";

export default {
  components: {},
  props: ["user","setting"],
  setup() {
    const { ctx } = getCurrentInstance();
  },
};
</script>

<style>
.haoce-user-card {
  text-align: left;
}
</style>