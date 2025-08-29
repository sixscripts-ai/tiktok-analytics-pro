// Initialize GSAP ScrollTrigger
gsap.registerPlugin(ScrollTrigger);

// DOM Elements
const navbar = document.querySelector('.navbar');
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');
const modal = document.getElementById('paymentModal');
const paymentForm = document.getElementById('payment-form');
const cardElement = document.getElementById('card-element');
const cardErrors = document.getElementById('card-errors');

    // Stripe Configuration
    const stripe = Stripe('pk_live_51N33AxKmi8Gn1BPTNziULKYrITOH41zdfechULL1OaTUkOcEG2IKwv3sEehRbjCYM6f8a6uabNEGh6rtyTSPlpv800xF9Sux7y');
const elements = stripe.elements();

// Initialize Stripe Elements
const card = elements.create('card', {
    style: {
        base: {
            fontSize: '16px',
            color: '#1a1a1a',
            '::placeholder': {
                color: '#aab7c4',
            },
        },
        invalid: {
            color: '#dc3545',
        },
    },
});

card.mount('#card-element');

// Card validation
card.addEventListener('change', function(event) {
    if (event.error) {
        cardErrors.textContent = event.error.message;
    } else {
        cardErrors.textContent = '';
    }
});

// Plan configurations
const plans = {
    creator: {
        name: 'Creator Plan',
        price: '$97/month',
        features: [
            'Advanced analytics dashboard',
            'Up to 3 accounts',
            'Real-time earnings tracking',
            'Viral content prediction',
            'Optimal posting times',
            'Email support'
        ]
    },
    pro: {
        name: 'Pro Plan',
        price: '$197/month',
        features: [
            'Everything in Creator +',
            'Up to 8 accounts',
            'AI-powered content optimization',
            'Competitor analysis & benchmarking',
            'Brand deal valuation',
            'Priority support (12h response)',
            'Custom reports & exports'
        ]
    },
    agency: {
        name: 'Agency Plan',
        price: '$397/month',
        features: [
            'Everything in Pro +',
            'Up to 15 accounts',
            'White-label reports',
            'API access & webhooks',
            'Dedicated support (4h response)',
            'Custom integrations'
        ]
    }
};

// Smooth scrolling function
function smoothScrollTo(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Scroll to pricing section
function scrollToPricing() {
    const pricingSection = document.getElementById('pricing');
    smoothScrollTo(pricingSection);
}

// Open demo modal
function openDemo() {
    // For now, just show an alert. You can replace this with actual video modal
    alert('Demo video would open here. Replace with actual video player implementation.');
}

// Select plan and open payment modal
function selectPlan(planType) {
    const plan = plans[planType];
    if (!plan) return;

    // Update modal content
    document.getElementById('selectedPlanName').textContent = plan.name;
    document.querySelector('.plan-price').textContent = plan.price;
    
    const featuresList = document.getElementById('selectedPlanFeatures');
    featuresList.innerHTML = '';
    plan.features.forEach(feature => {
        const li = document.createElement('li');
        li.textContent = feature;
        featuresList.appendChild(li);
    });

    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close modal
function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Free trial function
function startFreeTrial() {
    // Show a simple form for free trial
    const modal = document.getElementById('paymentModal');
    const modalContent = modal.querySelector('.modal-content');
    
    modalContent.innerHTML = `
        <div class="modal-header">
            <h3>Start Your Free Trial</h3>
            <span class="close" onclick="closeModal()">&times;</span>
        </div>
        <div class="modal-body">
            <div class="trial-summary">
                <h4>3-Day Free Trial</h4>
                <div class="trial-price">$0 - No credit card required</div>
                <div class="trial-features-compact">
                    <span>✓ Full Pro plan access</span>
                    <span>✓ Up to 3 accounts</span>
                    <span>✓ All analytics features</span>
                    <span>✓ Cancel anytime</span>
                </div>
            </div>
            <form id="trial-form">
                <div class="form-group">
                    <label for="trial-email">Email Address</label>
                    <input type="email" id="trial-email" required>
                </div>
                <div class="form-group">
                    <label for="trial-username">TikTok Username</label>
                    <input type="text" id="trial-username" placeholder="@yourusername" required>
                </div>
                <button type="submit" class="btn-primary btn-full">
                    <i class="fas fa-rocket"></i>
                    Start Free Trial
                </button>
            </form>
        </div>
    `;
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Handle trial form submission
    document.getElementById('trial-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('trial-email').value;
        const username = document.getElementById('trial-username').value;
        
        // Simulate trial creation
        alert(`Free trial started for ${email}! You'll receive login credentials shortly.`);
        closeModal();
    });
}

// Handle payment form submission
paymentForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const submitButton = paymentForm.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    // Show loading state
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    submitButton.disabled = true;

           try {
           const email = document.getElementById('email').value;
           const tiktokUsername = document.getElementById('tiktok-username').value;

           // Get plan details
           const selectedPlan = document.getElementById('selectedPlanName').textContent;
           const planPrice = document.querySelector('.plan-price').textContent;
           const amount = parseFloat(planPrice.replace(/[^0-9.]/g, ''));

           // Create payment intent on server
           const response = await fetch('/create-payment-intent', {
               method: 'POST',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify({
                   amount: amount,
                   currency: 'usd',
                   metadata: {
                       email: email,
                       tiktok_username: tiktokUsername,
                       plan: selectedPlan
                   }
               }),
           });

           const { clientSecret, error } = await response.json();

           if (error) {
               cardErrors.textContent = error;
               return;
           }

           // Confirm payment with Stripe
           const { error: confirmError } = await stripe.confirmCardPayment(clientSecret, {
               payment_method: {
                   card: card,
                   billing_details: {
                       email: email,
                   },
               }
           });

           if (confirmError) {
               cardErrors.textContent = confirmError.message;
               return;
           }

           // Payment successful
           alert('Payment successful! Welcome to TikTok Analytics Pro!');
           closeModal();
           paymentForm.reset();

    } catch (error) {
        console.error('Payment error:', error);
        cardErrors.textContent = 'An error occurred. Please try again.';
    } finally {
        // Reset button state
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
});

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target === modal) {
        closeModal();
    }
});

// Mobile menu toggle
function toggleMobileMenu() {
    navMenu.classList.toggle('active');
    navToggle.classList.toggle('active');
}

// Navbar scroll effect
window.addEventListener('scroll', function() {
    if (window.scrollY > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Animate numbers on scroll
function animateNumbers() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-target'));
        const suffix = stat.textContent.includes('$') ? '$' : '';
        const suffix2 = stat.textContent.includes('K') ? 'K' : '';
        const suffix3 = stat.textContent.includes('%') ? '%' : '';
        
        gsap.to(stat, {
            innerHTML: target,
            duration: 2,
            ease: "power2.out",
            snap: { innerHTML: 1 },
            onUpdate: function() {
                const current = Math.floor(this.targets()[0].innerHTML);
                stat.innerHTML = suffix + current.toLocaleString() + suffix2 + suffix3;
            }
        });
    });
}

// Floating elements animation
function initFloatingElements() {
    const floatingCards = document.querySelectorAll('.floating-card');
    
    floatingCards.forEach((card, index) => {
        const speed = parseFloat(card.getAttribute('data-speed')) || 0.5;
        
        gsap.to(card, {
            y: -20,
            duration: 2 + index,
            ease: "power2.inOut",
            yoyo: true,
            repeat: -1,
            delay: index * 0.5
        });
    });
}

// Feature cards animation
function initFeatureCards() {
    gsap.from('.feature-card', {
        duration: 0.8,
        y: 50,
        opacity: 0,
        stagger: 0.2,
        ease: "power2.out",
        scrollTrigger: {
            trigger: '.features-grid',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    });
}

// Pricing cards animation
function initPricingCards() {
    gsap.from('.pricing-card', {
        duration: 0.8,
        y: 50,
        opacity: 0,
        stagger: 0.2,
        ease: "power2.out",
        scrollTrigger: {
            trigger: '.pricing-grid',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    });
}

// Testimonial cards animation
function initTestimonialCards() {
    gsap.from('.testimonial-card', {
        duration: 0.8,
        y: 50,
        opacity: 0,
        stagger: 0.2,
        ease: "power2.out",
        scrollTrigger: {
            trigger: '.testimonials-grid',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    });
}

// Hero section animation
function initHeroAnimation() {
    const tl = gsap.timeline();
    
    tl.from('.hero-badge', {
        duration: 0.8,
        y: -30,
        opacity: 0,
        ease: "power2.out"
    })
    .from('.hero-title', {
        duration: 1,
        y: 50,
        opacity: 0,
        ease: "power2.out"
    }, '-=0.4')
    .from('.hero-subtitle', {
        duration: 0.8,
        y: 30,
        opacity: 0,
        ease: "power2.out"
    }, '-=0.6')
    .from('.hero-stats', {
        duration: 0.8,
        y: 30,
        opacity: 0,
        ease: "power2.out"
    }, '-=0.4')
    .from('.hero-buttons', {
        duration: 0.8,
        y: 30,
        opacity: 0,
        ease: "power2.out"
    }, '-=0.4')
    .from('.dashboard-preview', {
        duration: 1,
        x: 100,
        opacity: 0,
        ease: "power2.out"
    }, '-=0.8');
}

// Analytics section animation
function initAnalyticsAnimation() {
    gsap.from('.analytics-text', {
        duration: 0.8,
        x: -50,
        opacity: 0,
        ease: "power2.out",
        scrollTrigger: {
            trigger: '.analytics-content',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    });
    
    gsap.from('.analytics-visual', {
        duration: 0.8,
        x: 50,
        opacity: 0,
        ease: "power2.out",
        scrollTrigger: {
            trigger: '.analytics-content',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    });
}

// Demo section animation
function initDemoAnimation() {
    gsap.from('.demo-text', {
        duration: 0.8,
        x: -50,
        opacity: 0,
        ease: "power2.out",
        scrollTrigger: {
            trigger: '.demo-content',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    });
    
    gsap.from('.demo-video', {
        duration: 0.8,
        x: 50,
        opacity: 0,
        ease: "power2.out",
        scrollTrigger: {
            trigger: '.demo-content',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    });
}

// CTA section animation
function initCTAAnimation() {
    gsap.from('.cta-content', {
        duration: 0.8,
        y: 50,
        opacity: 0,
        ease: "power2.out",
        scrollTrigger: {
            trigger: '.cta',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    });
}

// Initialize all animations
document.addEventListener('DOMContentLoaded', function() {
    // Register GSAP plugins
    gsap.registerPlugin(ScrollTrigger);
    
    // Fallback: Ensure all content is visible after 2 seconds
    setTimeout(() => {
        gsap.set('.feature-card, .pricing-card, .testimonial-card, .analytics-text, .demo-text, .cta-content', {
            opacity: 1,
            y: 0
        });
    }, 2000);
    
    // Initialize animations
    initHeroAnimation();
    initFloatingElements();
    initFeatureCards();
    initPricingCards();
    initTestimonialCards();
    initAnalyticsAnimation();
    initDemoAnimation();
    initCTAAnimation();
    
    // Animate numbers when they come into view
    ScrollTrigger.create({
        trigger: '.hero-stats',
        start: 'top 80%',
        onEnter: animateNumbers
    });
    
    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                smoothScrollTo(target);
            }
        });
    });
});

// Add CSS for mobile menu
const style = document.createElement('style');
style.textContent = `
    @media (max-width: 768px) {
        .nav-menu {
            position: fixed;
            top: 100%;
            left: 0;
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            flex-direction: column;
            padding: 2rem;
            transform: translateY(-100%);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .nav-menu.active {
            transform: translateY(0);
            opacity: 1;
            visibility: visible;
        }
        
        .nav-toggle.active span:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }
        
        .nav-toggle.active span:nth-child(2) {
            opacity: 0;
        }
        
        .nav-toggle.active span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
    }
    
    .navbar.scrolled {
        background: rgba(255, 255, 255, 0.98);
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    }
`;
document.head.appendChild(style);
