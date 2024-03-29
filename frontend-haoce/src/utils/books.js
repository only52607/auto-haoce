import {
    getCurrentInstance,
    reactive,
    ref,
    computed,
    watch,
    watchEffect,
} from "vue";
import api from "@/utils/api.js"

let books = ref({})

let bookDatas = reactive({})

async function updateBooks(){
    books.value = (await api.get("/books/")).data
}

async function updateBookData(bookId){
    if (bookId==0) return 
    bookDatas[bookId] = (await api.get(`/books/${bookId}/data`)).data
    bookDatas[bookId].chapters_view_data = (await api.get(`/books/${bookId}/chapters_view_data`)).data
}

export default {
    books,bookDatas,updateBooks,updateBookData
}