
    // Hamburger nav
    const navToggle = document.getElementById("navToggle");
    const navMenu = document.getElementById("navMenu");
    navToggle.onclick = () => navMenu.classList.toggle("open");
    // Modal
    const loginBtn = document.getElementById("loginBtn");
    const loginModal = document.getElementById("loginModal");
    const closeModal = document.getElementById("closeModal");
    loginBtn.onclick = () => { loginModal.classList.add("show"); }
    closeModal.onclick = () => { loginModal.classList.remove("show"); }
    window.onclick = (e) => { if(e.target === loginModal) loginModal.classList.remove("show"); }
    // Password toggle
    const pw = document.getElementById("loginPassword");
    const tgl = document.getElementById("togglePassword");
    tgl.onclick = () => {
        pw.type = pw.type === "password" ? "text":"password";
        tgl.innerHTML = pw.type==="password" ? '<i class="ri-eye-line"></i>' : '<i class="ri-eye-off-line"></i>';
    }
    // Theme toggling
    const themeToggle = document.getElementById("themeToggle");
    const body = document.body;
    const moon = '<i class="ri-moon-fill"></i>'; const sun = '<i class="ri-sun-fill"></i>';
    let mode = localStorage.getItem("theme") || "light";
    if(mode !== body.getAttribute("data-theme")) {
        body.setAttribute("data-theme", mode);
        themeToggle.innerHTML = mode==="dark"?sun:moon;
    }
    themeToggle.onclick = () => {
        const t = body.getAttribute("data-theme") === "dark" ? "light" : "dark";
        body.setAttribute("data-theme", t);
        localStorage.setItem("theme", t);
        themeToggle.innerHTML = t==="dark"?sun:moon;
    }
    // Loader fade-out
    window.addEventListener("load", ()=>{
        document.querySelector(".loader-img")?.style.setProperty("display","none");
    });
    // Section scroll-reveal
    function inView(el) {
        return el.getBoundingClientRect().top < window.innerHeight * .92;
    }
    function revealSections() {
        document.querySelectorAll(".reveal").forEach(el=>{
            if (inView(el)) el.classList.add("visible");
        });
    }
    window.addEventListener("scroll",revealSections); window.addEventListener("load",revealSections);
    // Login form
    const loginForm = document.getElementById("loginForm");
    loginForm.onsubmit = (e)=>{
        e.preventDefault();
        loginModal.classList.remove("show");
        loginForm.reset();
        setTimeout(()=>alert("Login successful! (Simulation)"),800);
    }
    // Navbar Scroll Effect
    const navbar = document.getElementById("navbar");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });
    // Button Ripple Effect
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const circle = document.createElement('span');
            const diameter = Math.max(this.clientWidth, this.clientHeight);
            const radius = diameter / 2;
            circle.style.width = circle.style.height = `${diameter}px`;
            circle.style.left = `${e.clientX - this.offsetLeft - radius}px`;
            circle.style.top = `${e.clientY - this.offsetTop - radius}px`;
            circle.classList.add('ripple');
            this.appendChild(circle);
            circle.addEventListener('animationend', () => {
                circle.remove();
            });
        });
    });
    // 3D Feature Card Mouse-Tilt
    document.querySelectorAll('.feature').forEach(card => {
      card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        card.style.transform = `rotateY(${x*16}deg) rotateX(${-y*10}deg) scale(1.06)`;
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });