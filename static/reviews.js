function postArticle() {
    url = $('#post-url').val()
    comment = $('#post-comment').val()
    studyOption = $('input[name=studyOption]:checked').val();
    console.log(studyOption);
    $.ajax({
        type: "POST",
        url: "/review",
        data: {url_give: url, comment_give: comment, studyOption_give: studyOption},
        success: function (response) { // 성공하면
            alert(response["msg"]);
            window.location.reload();
        }
    })
}

function sign_out() {
    $.removeCookie('mytoken', {path: '/'});
    alert('로그아웃!')
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

function checkSection(){
    let check_section = []
    $("input[name=studyOption]:checked").each(function (){
        check_section.push($(this).val());
    })


}