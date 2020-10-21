<template>
  <a-row
    type="flex"
    justify="center"
    align="top"
    :bordered="false"
    style="width: 100%;height: 100%"
  >
    <a-col :xs="24" :sm="20" :md="12" :lg="8" :xl="6" style="align-self:center">
      <a-card title="好策 - 登录">
        <a-form :model="formAuth" :rules="rules" :wrapperCol="{span: 24}">
          <a-form-item name="username">
            <input-account placeholder="用户名" v-model:value="formAuth.username" />
          </a-form-item>
          <a-form-item name="password">
            <input-password placeholder="密码" v-model:value="formAuth.password" />
          </a-form-item>
          <a-button type="primary" @click="authenticate" :loading="isAuthenticating">登录</a-button>
        </a-form>
      </a-card>
    </a-col>
  </a-row>
</template>

<script>
import InputAccount from "@/components/inputs/InputAccount.vue";
import InputPassword from "@/components/inputs/InputPassword.vue";
import { getCurrentInstance, reactive, ref } from "vue";
export default {
  name: "Auth",
  setup() {
    const { ctx } = getCurrentInstance();
    const formAuth = reactive({
      username: "",
      password: "",
    });
    const isAuthenticating = ref(false);
    const rules = reactive({});
    async function authenticate() {
      isAuthenticating.value = true;
      try {
        let result = await ctx.$api({
          method: "post",
          url: "/auth",
          transformRequest: [
            function (oldData) {
              let newStr = "";
              for (let item in oldData) {
                newStr +=
                  encodeURIComponent(item) +
                  "=" +
                  encodeURIComponent(oldData[item]) +
                  "&";
              }
              newStr = newStr.slice(0, -1);
              return newStr;
            },
          ],
          data: formAuth,
        });
        ctx.$message.success("验证通过", 2);
        ctx.$router.replace("/");
      } catch (err) {
        console.log(err);
        ctx.$error({ title: "验证失败" });
      }
      isAuthenticating.value = false;
    }
    return {
      formAuth,
      isAuthenticating,
      rules,
      authenticate,
    };
  },
  components: {
    InputAccount,
    InputPassword,
  },
};
</script>

<style>
</style>
