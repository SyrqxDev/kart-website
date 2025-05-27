function showabout(){
    $("#about_container").css("display","inherit");
    $("#about_container").addClass("animated slideInLeft");
    setTimeout(function(){
        $("#about_container").removeClass("animated slideInLeft");
    },800);
}
function closeabout(){
    $("#about_container").addClass("animated slideOutLeft");
    setTimeout(function(){
        $("#about_container").removeClass("animated slideOutLeft");
        $("#about_container").css("display","none");
    },800);
}
function showwork(){
    $("#work_container").css("display","inherit");
    $("#work_container").addClass("animated slideInRight");
    setTimeout(function(){
        $("#work_container").removeClass("animated slideInRight");
    },800);
}
function closework(){
    $("#work_container").addClass("animated slideOutRight");
    setTimeout(function(){
        $("#work_container").removeClass("animated slideOutRight");
        $("#work_container").css("display","none");
    },800);
}
function showcontact(){
    $("#contact_container").css("display","inherit");
    $("#contact_container").addClass("animated slideInUp");
    setTimeout(function(){
        $("#contact_container").removeClass("animated slideInUp");
    },800);
}
function closecontact(){
    $("#contact_container").addClass("animated slideOutDown");
    setTimeout(function(){
        $("#contact_container").removeClass("animated slideOutDown");
        $("#contact_container").css("display","none");
    },800);
}
setTimeout(function(){
    $("#loading").addClass("animated fadeOut");
    setTimeout(function(){
      $("#loading").removeClass("animated fadeOut");
      $("#loading").css("display","none");
      $("#box").css("display","none");
      $("#about").removeClass("animated fadeIn");
      $("#contact").removeClass("animated fadeIn");
      $("#work").removeClass("animated fadeIn");
    },1000);
},1500);
const images = [
    { url: '/assets/img/20250501_143950000_iOS.jpg', position: 'center center' },
    { url: '/assets/img/20250426_194717326_iOS.jpg', position: 'bottom center' },
    { url: '/assets/img/20250425_230000000_iOS 2.jpg', position: 'center bottom' },
    { url: '/assets/img/20250426_192557126_iOS.jpg', position: 'center bottom' },
    { url: '/assets/img/20250426_192612741_iOS.jpg', position: 'center bottom' },
    { url: '/assets/img/img2.jpeg', position: 'center center' },
    { url: '/assets/img/img3.jpeg', position: 'center center' },
    { url: '/assets/img/img4.jpeg', position: 'center center' },
    { url: '/assets/img/img5.jpeg', position: 'center center' },
    { url: '/assets/img/img6.jpeg', position: 'center center' },
    { url: '/assets/img/img7.jpeg', position: 'center center' },
    { url: '/assets/img/img8.jpeg', position: 'center center' },

];

const slideshowContainer = document.getElementById('slideshow');
let slides = [];
let current = 0;

// Create slides dynamically
images.forEach((img, index) => {
    const slide = document.createElement('div');
    slide.classList.add('slide');
    slide.style.backgroundImage = `url('${encodeURIComponent(img.url)}')`;
    slide.style.backgroundPosition = img.position;
    if (index === 0) slide.classList.add('active');
    slideshowContainer.appendChild(slide);
    slides.push(slide);
});

// Crossfade logic
setInterval(() => {
    slides[current].classList.remove('active');
    current = (current + 1) % slides.length;
    slides[current].classList.add('active');
}, 5000);