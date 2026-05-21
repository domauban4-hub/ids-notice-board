const slideDelay = 15000;
let slideIndex = -1;
let slideTimer = null;

function updateDateTime() {
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const date = now.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
    document.getElementById('time').textContent = time;
    document.getElementById('date').textContent = date;
    const slideTime = document.getElementById('slide-time');
    const slideDate = document.getElementById('slide-date');
    if (slideTime) slideTime.textContent = time;
    if (slideDate) slideDate.textContent = date;
}

function showDashboard() {
    const dashboard = document.getElementById('dashboard-panel');
    const slideshow = document.getElementById('slide-panel');
    if (!dashboard || !slideshow) return;
    dashboard.classList.remove('hidden');
    slideshow.classList.add('hidden');
    scheduleNextSlide();
}

function showSlide(index) {
    const dashboard = document.getElementById('dashboard-panel');
    const slideshow = document.getElementById('slide-panel');
    const slideImage = document.getElementById('slide-image');
    const slideCounter = document.getElementById('slide-counter');
    const slides = window.slideData || [];
    if (!slides.length || !slideshow || !slideImage || !slideCounter) {
        return showDashboard();
    }
    slideIndex = index % slides.length;
    const slide = slides[slideIndex];
    if (!slide) return showDashboard();

    slideImage.src = slide.src;
    slideCounter.textContent = `Slide ${slideIndex + 1} of ${slides.length}`;
    dashboard.classList.add('hidden');
    slideshow.classList.remove('hidden');
    slideTimer = setTimeout(() => showSlide(slideIndex + 1), slideDelay);
}

function scheduleNextSlide() {
    clearTimeout(slideTimer);
    slideTimer = setTimeout(() => showSlide(0), slideDelay);
}

function buildSlides() {
    const slideJson = document.getElementById('slides-data');
    if (!slideJson) return [];
    try {
        const slides = JSON.parse(slideJson.textContent);
        return slides.map(slide => ({ src: slide.src }));
    } catch (error) {
        return [];
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.slideData = buildSlides();
    updateDateTime();
    setInterval(updateDateTime, 1000);
    scheduleNextSlide();
});
