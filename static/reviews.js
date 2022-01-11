function postArticle() {
    url = $('#post-url').val()
    comment = $('#post-comment').val()
    studyOption = $('input[name=studyOption]:checked').val();
    console.log(studyOption);
    $.ajax({
        type: "POST",
        url: "/reviews",
        data: {url_give: url, comment_give: comment, studyOption_give: studyOption},
        success: function (response) { // 성공하면
            alert("리뷰 작성 완료")
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
