function checkUrlForm(strUrl) {
    var expUrl = /^http[s]?\:\/\//i;
    return expUrl.test(strUrl);
}


function postArticle() {
    if (getCookie('mytoken') != null) {
        url = $('#post-url').val()
        comment = $('#post-comment').val()
        studyOption = $('input[name=studyOption]:checked').val();
        if (url == "") {
            alert("리뷰할 url이 비어있습니다!")
        } else if (studyOption == undefined) {
            alert("분야를 선택해주세요!")
        } else if (!checkUrlForm(url)){
            alert("url 형식을 확인해주세요!")
        } else {
            console.log(studyOption);
            $.ajax({
                type: "POST",
                url: "/",
                data: {url_give: url, comment_give: comment, studyOption_give: studyOption},
                success: function (response) { // 성공하면
                    alert("리뷰 작성 완료")
                    window.location.href = "/";
                }
            })
        }
    } else {
        alert("회원가입을 해주세요!")
        window.location.href = "/login"
    }

}
function gologin(){
    if (getCookie('mytoken') != null){
        alert("이미 로그인이 되어있습니다,")
    }else{
        window.location.href='/login'
    }
}

function getCookie(cookieName) {
    var cookieValue = null;
    if (document.cookie) {
        var array = document.cookie.split((escape(cookieName) + '='));
        if (array.length >= 2) {
            var arraySub = array[1].split(';');
            cookieValue = unescape(arraySub[0]);
        }
    }
    return cookieValue;
}

function mypage() {
    if (getCookie('mytoken') != null) {
        window.location.href = '/mypage'
    } else {
        alert("회원가입을 해주세요!")
        window.location.href = "/login"
    }
}

function sign_out() {
    if ($.removeCookie('mytoken', {path: '/'})) {
        alert('로그아웃!')
    } else {
        alert("로그인정보가 없습니다!")
    }
    window.location.href = "/login"

}

function likeReview(number) {

    $.ajax({
        type: 'POST',
        url: '/reviews/like',
        data: {number_give: number},
        success: function (response) {
            alert(response['msg']);
            window.location.reload();
        }
    });
}

let option = "None";

function filter() {
    let new_filter = ($("select[name=studyOption]").val());

    if (option == new_filter) {
        return;
    } else {
        option = new_filter;
        console.log(option)
        $.ajax({
            type: 'GET',
            url: `/reviews/section?option=${option}`,
            data: {},
            success: function (response) {
                window.location.href = `/reviews/section?option=${option}`
            }
        });
    }


}
