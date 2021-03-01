/*
<!--인증번호 검증과정-->
<script>
var uname = getParameterByName('name');
swal({
    title: "등록해제",
    text: "등록을 해제하려면,\n 핸드폰으로 받은 인증번호를 입력해 주세요.\n(수신까지 최대 1분 소요)",
    icon: "info",
    buttons: {
        cancel: "취소",
        confirm: "인증번호 확인",
    },
    content: {
        element: "input",
    attributes: {
            placeholder: "xxxxx",
            type: "text",
            required: "required"
        },
    },
    closeOnClickOutside: false,
    closeOnEsc: false,
}).then((value) => {

    if (value.length > 3 && !isNaN(value)){
    post_to_url("https://api.leok.kr/chk",{'ccode':value,'rdata':uname})
}else{
      swal({
        title: "올바르지 않은 형식",
        text: "옯바르지 않은 글자를 입력하셨거나,\n너무 짧습니다\n다시 입력하려면 새로고침 하세요.",
        icon: "error",
        timer: 3000,
        buttons: false,
        dangerMode: false,
    })
}
});
</script>




<!--인증번호 입력 재시도-->>
<script>
var uname = getParameterByName('name');
swal({
    title: "등록해제",
    text: "올바르지 않은 인증번호 입니다.\n\n등록을 해제하려면,\n 핸드폰으로 받은 인증번호를 입력해 주세요.",
    icon: "warning",
    buttons: {
        cancel: "취소",
        confirm: "인증번호 확인",
    },
    content: {
        element: "input",
    attributes: {
            placeholder: "xxxxx",
            type: "text",
            required: "required"
        },
    },
    closeOnClickOutside: false,
    closeOnEsc: false,
}).then((value) => {

    if (value.length > 3 && !isNaN(value)){
    post_to_url("https://api.leok.kr/chk",{'ccode':value,'rdata':uname})
}else{
      swal({
        title: "올바르지 않은 형식",
        text: "옯바르지 않은 글자를 입력하셨거나,\n너무 짧습니다\n다시 입력하려면 새로고침 하세요.",
        icon: "error",
        timer: 3000,
        buttons: false,
        dangerMode: false,
    })
}
});
</script>



<!--등록해제 성공-->>
<script>

swal({
title: "등록해제 성공!",
text: "유저의 모든 정보를 DB에서\n영구히 삭제하였습니다.\n\n 앞으로는 7:30분에 \n자가진단이 수행되지 않습니다.",
icon: "success",
showCancelButton: false,
showConfirmButton: true,
dangerMode: false,

})
</script>


<!--등록해제 실패(올바르지 않은 전화번호)-->
<script>

swal({
title: "등록해제 실패",
text: "번호를 등록하지 않은 유저이거나,\n 잘못된 번호를 등록하였습니다. \n support@leok.kr 로 메일을 보내\n 수동 해제 가능합니다.",
icon: "warning",
showCancelButton: false,
showConfirmButton: true,
dangerMode: false,

})
</script>


<!--등록해제 실패(등록되지 않은 유저)-->>
<script>

swal({
title: "등록해제 실패",
text: "유저정보를 찾을수 없습니다.\n 등록되지 않은 유저이거나,\n `생년월일 이름`을 잘못 입력하였습니다\n 다시 시도하십시오.",
icon: "error",
showCancelButton: false,
showConfirmButton: true,
dangerMode: false,

})
</script>



<!--등록실패: 찾을수 없는 학교-->>
<script>

swal({
title: "등록 실패",
text: "찾을수 없는 학교입니다.\n 교육청과 학교명을 올바르게 입력했는지 \n다시 한번 확인해 주세요.",
icon: "error",
showCancelButton: false,
showConfirmButton: true,
dangerMode: false,

})
</script>
<!--등록실패: 올바르지 않은 학생정보-->>
<script>

swal({
title: "등록 실패",
text: "학생정보가 올바르지 않습니다.\n 학교정보는 올바르나, 학생인증에 실패하였습니다.\n 다시 한번 확인해 주세요.",
icon: "error",
showCancelButton: false,
showConfirmButton: true,
dangerMode: false,

})
</script>

<!--등록실패: 올바르지 않은 비밀번호-->
<script>

swal({
title: "등록 실패",
text: "비밀번호가 올바르지 않거나, 너무 많이 틀렸습니다.\n 다시 한번 확인후 입력해 주세요.",
icon: "error",
showCancelButton: false,
showConfirmButton: true,
dangerMode: false,

})
</script>

<!--등록성공-->
<script>

swal({
title: "등록 성공!",
text: "성공적으로 등록되었습니다!\n 매일 KST 오전 7:30분에 자동으로 자가진단을 수행합니다!\n등록 해제는 밑의 버튼을 눌러주세요!",
icon: "success",
showCancelButton: false,
showConfirmButton: true,
dangerMode: false,

})
</script>
<!--이미 등록됨-->
<script>

swal({
title: "이미 등록되었습니다! / 비밀번호 입력 대상이 아닙니다!",
text: "**비밀번호 입력 대상이 아닙니다!**\n이미 등록되어 있는 학생정보 입니다!\n매일 KST 오전 7:30분에 자동으로 자가진단을 수행합니다!\n등록 해제는 밑의 버튼을 눌러주세요!",
icon: "warning",
showCancelButton: false,
showConfirmButton: true,
dangerMode: false,

})
</script>
*/

var form = document.querySelector("#MainForm")
var name = form.name
var region = form.region
var level = form.level
var schoolname = form.schoolname
var birthday = form.birthday
var password = form.password
var phonenumber = form.phonenumber


var isTouchDevice = (navigator.maxTouchPoints || 'ontouchstart' in document.documentElement);
console.log(isTouchDevice)
// 모바일에서 로고 숨기기
if (isTouchDevice){
    document.getElementById("logoimage").style.display = "none";
}


//onSubmit Function
function onSubmit(event) {
    event.preventDefault();

    swal({
        title: "이용약관(개인정보 처리방침)",
        text: "\n1.해당 기능을 이용함으로써 생기는 피해와\n 그에 대한 책임은 모두 이용자에게 있습니다.\n\n2.사용자의 개인정보는 안전하게 보관되며\n '건강상태 자가진단' 이외의 목적으로 \n사용되지 않습니다\n 또한,등록해제시 즉시 파기됩니다.\n\n3.몸의 이상이 있거나, 자가진단에 항목에\n 해당되는 증상이 있을경우\n이용자는 7시 10분 이후\n 자가진단을 수행하여야 합니다.",
        icon: "success",
        buttons: ["취소", "이용약관에 동의하며 제출합니다."]
    }).then((YES) => {
        if (YES) {
            var postdata = {
                "name": form.name.value,
                "password": form.password.value,
                "level": form.level.value,
                "region": form.region.value,
                "phonenumber": form.phonenumber.value,
                "birthday": form.birthday.value,
                "schoolname": form.schoolname.value
            }
            $.post("RegisterHCS", postdata, function (data) {
                console.log(data)
                var title = NaN;
                var icon = NaN;
                if (!data.error) {
                    title = "등록 성공!";
                    icon = "success";
                    form.reset()
                } else if (data.code == "ALREADY") {
                    title = "이미 등록되었습니다!";
                    icon = "warning";
                    form.reset()
                } else {
                    title = "등록 실패";
                    icon = "error"
                }
                swal({
                    title: title,
                    text: data.message,
                    icon: icon,
                })
            })

        }
    });
}


function Unregster() {
    swal({
        title: "등록해제",
        text: "등록을 해제하려면,\n 생년월일 6자를 입력해주세요.",
        icon: "info",
        buttons: {
            cancel: "취소",
            confirm: "다음",
        },
        content: {
            element: "input",
            attributes: {
                placeholder: "xxxxxx",
                type: "tel",
                required: "required"
            },
        },
        closeOnClickOutside: false,
        closeOnEsc: false,
    }).then((birthday) => {
        if (birthday) {
            swal({
                title: "등록해제",
                text: "등록해제를 계속하려면,\n 이름을 입력해주세요.",
                icon: "info",
                buttons: {
                    cancel: "취소",
                    confirm: "다음",
                },
                content: {
                    element: "input",
                    attributes: {
                        placeholder: "홍길동",
                        type: "text",
                        required: "required"
                    },
                },
                closeOnClickOutside: false,
                closeOnEsc: false,
            }).then((name) => {
                if (name) {
                    swal({
                        title: "등록해제",
                        text: "등록해제를 계속하려면,\n 자가진단 비밀번호(4자, 숫자)를 입력해주세요.",
                        icon: "info",
                        buttons: {
                            cancel: "취소",
                            confirm: "등록해제",
                        },
                        content: {
                            element: "input",
                            attributes: {
                                placeholder: "xxxx",
                                type: "tel",
                                required: "required"
                            },
                        },
                        closeOnClickOutside: false,
                        closeOnEsc: false,
                    }).then((password) => {
                        $.post("UnregisterHCS", {
                            birthday,
                            name,
                            password
                        }, function (data) {
                            console.log(data)
                            if (data.error){
                                swal({
                                    title: "등록해제 실패",
                                    text: data.message,
                                    icon: "error",
                                })
                            }else{
                                swal({
                                    title: "등록해제 성공!",
                                    text: data.message,
                                    icon: "success",
                                })
                            }
                            
                        })
                    })
                }
            })
        }
    });
}


//Init
function init() {
    document.querySelector("#unreg_button").addEventListener("click", Unregster)
    form.addEventListener("submit", onSubmit)
}

init()