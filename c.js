export async function getCityList(){
	return await request({
		url:"/cities",
	})
}

const cities=ref([]);

onMounted(async () => {
  const res = await getCityList();
  cities.value = res.data
});



const getKeywordGoodsCount = async (keyword) => {
  const res = await getKeywordGoodsCountData(keyword);
  goodsCount.value = res;
};


http://127.0.0.1:8000/user/code?email=3311384165@qq.com
export async function getEmailCode(email) {
  return await request({
    url: "/user/code",
    method: "get",
    params: {
      email: email
    }
  })
}


const email = ref("3311384165@qq.com")
// 点击发送验证码
const handleSendCode = async () => {
  const res = await getEmailCode(email.value)

  if (res.status === 200) {
    alert("发送成功")
  } else {
    alert(res.data)
  }
}