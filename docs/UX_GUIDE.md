# UX va Static Fayllar - To'liq Qo'llanma

## 📦 Yaratilgan Fayllar

### JavaScript (static/js/)
1. **main.js** (9.5 KB)
   - Toast notification system
   - Loading overlay
   - Back to top button
   - Smooth scroll
   - Form enhancements
   - Lazy loading
   - Copy to clipboard
   - Confirm dialogs
   - AJAX helper functions

2. **forms.js** (4.2 KB)
   - Real-time form validation
   - Character counter
   - Password strength indicator
   - File upload preview

### CSS (static/css/)
1. **custom.css** (8.7 KB)
   - Toast notification styles
   - Loading spinner
   - Back to top button
   - Smooth transitions
   - Skeleton loading
   - Button effects
   - Responsive design

2. **animations.css** (2.1 KB)
   - Pulse, floating, fade-in
   - Typing indicator
   - Card entrance animations
   - Gradient text effects

### Images (static/images/)
1. **logo.svg** - Platform logotipi (200x200)
2. **favicon.svg** - Browser favicon (64x64)

### Templates
1. **templates/base.html** - Yangilandi (static fayllar ulandi)
2. **templates/core/ux_demo.html** - Demo sahifa

## 🚀 Ishlatish

### 1. Toast Notifications

```javascript
// Success
Toast.success('Maqola muvaffaqiyatli saqlandi!');

// Error
Toast.error('Xatolik yuz berdi!');

// Warning
Toast.warning('Diqqat! Bu amal qaytarilmaydi.');

// Info
Toast.info('Yangi xabar keldi', 'Bildirishnoma');

// Custom duration (milliseconds)
Toast.success('Message', 'Title', 3000);
```

### 2. Loading Overlay

```javascript
// Show loading
Loading.show();

// Hide loading
Loading.hide();

// Example with async operation
Loading.show();
fetch('/api/data')
    .then(response => response.json())
    .then(data => {
        Loading.hide();
        Toast.success('Ma\'lumot yuklandi!');
    })
    .catch(error => {
        Loading.hide();
        Toast.error('Xatolik yuz berdi');
    });
```

### 3. Form Validation

```html
<form class="needs-validation" novalidate>
    <div class="mb-3">
        <label class="form-label">Email *</label>
        <input type="email" class="form-control" required>
        <div class="invalid-feedback">
            Iltimos, to'g'ri email kiriting
        </div>
    </div>
    <button type="submit" class="btn btn-primary">Yuborish</button>
</form>
```

### 4. Character Counter

```html
<textarea class="form-control" maxlength="500"></textarea>
<!-- Counter avtomatik qo'shiladi -->
```

### 5. Password Strength

```html
<input type="password" name="password" class="form-control">
<!-- Strength indicator avtomatik qo'shiladi -->
```

### 6. File Preview

```html
<input type="file" class="form-control" accept="image/*">
<!-- Preview avtomatik ko'rsatiladi -->
```

### 7. Copy to Clipboard

```html
<button class="btn btn-secondary" data-copy="https://maqola.uz/article/123">
    <i class="bi bi-clipboard"></i> Nusxa olish
</button>
```

### 8. Confirm Dialog

```html
<button class="btn btn-danger" data-confirm="Rostdan ham o'chirmoqchimisiz?">
    <i class="bi bi-trash"></i> O'chirish
</button>
```

### 9. Smooth Scroll

```html
<a href="#section-id" class="btn btn-primary">
    Pastga o'tish
</a>
<!-- Avtomatik smooth scroll -->
```

### 10. Lazy Loading Images

```html
<img data-src="image.jpg" alt="Description" class="img-fluid">
<!-- Rasm faqat ko'rinishga kelganda yuklanadi -->
```

### 11. Skeleton Loading

```html
<div class="skeleton skeleton-title"></div>
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-avatar"></div>
```

### 12. Animations

```html
<!-- Fade in up -->
<div class="fade-in-up">Content</div>

<!-- Scale in -->
<div class="scale-in">Content</div>

<!-- Floating -->
<div class="floating">Content</div>

<!-- Pulse -->
<div class="pulse">Content</div>

<!-- Gradient text -->
<h1 class="gradient-text">Maqola</h1>
```

### 13. AJAX Form Submit

```javascript
const form = document.querySelector('#myForm');
submitFormAjax(form, 
    // Success callback
    (data) => {
        Toast.success(data.message);
        window.location.href = data.redirect;
    },
    // Error callback
    (error) => {
        Toast.error('Xatolik yuz berdi');
    }
);
```

## 🎨 CSS Classes

### Button States
- `.btn-loading` - Loading holatini ko'rsatadi
- `.ripple` - Ripple effekt

### Animations
- `.fade-in-up` - Pastdan yuqoriga fade
- `.scale-in` - Kichikdan kattaga
- `.floating` - Suzish animatsiyasi
- `.pulse` - Pulsatsiya
- `.shake` - Silkinish (xatolik uchun)

### Loading
- `.skeleton` - Skeleton placeholder
- `.skeleton-title` - Sarlavha skeleton
- `.skeleton-text` - Matn skeleton
- `.skeleton-avatar` - Avatar skeleton

## 📱 Responsive Design

Barcha elementlar mobil qurilmalarda to'g'ri ishlaydi:
- Toast notifications - to'liq kenglikda
- Back to top - kichikroq
- Forms - touch-friendly
- Animations - optimallashtirilgan

## ♿ Accessibility

- ARIA labels
- Keyboard navigation
- Focus visible
- Screen reader support
- Color contrast (WCAG AA)

## 🧪 Test Qilish

1. Serverni ishga tushiring:
```bash
python manage.py runserver
```

2. Demo sahifani oching:
```
http://localhost:8000/ux-demo/
```

3. Barcha funksiyalarni sinab ko'ring!

## 📊 Statistika

- **16 ta** UX feature
- **4 ta** JavaScript fayl
- **2 ta** CSS fayl
- **2 ta** SVG rasm
- **100%** responsive
- **0** dependencies (faqat Bootstrap va vanilla JS)

## 🔧 Sozlash

### Toast Duration
```javascript
// Default: 5000ms
Toast.success('Message', 'Title', 10000); // 10 seconds
```

### Loading Timeout
```javascript
Loading.show();
setTimeout(() => Loading.hide(), 30000); // 30 seconds max
```

### Scroll Threshold
```javascript
// Back to top button appears after 300px scroll
// Edit in main.js line ~100
```

## 💡 Maslahatlar

1. **Toast** - Foydalanuvchiga doimiy feedback bering
2. **Loading** - Uzoq operatsiyalarda ko'rsating
3. **Validation** - Real-time validation yoqing
4. **Animations** - Haddan oshirmaslik
5. **Accessibility** - ARIA labellarni unutmang

## 🐛 Debugging

Browser console'da:
```javascript
// Toast test
Toast.success('Test');

// Loading test
Loading.show();
setTimeout(() => Loading.hide(), 2000);

// Check if scripts loaded
console.log(typeof Toast); // should be 'object'
console.log(typeof Loading); // should be 'object'
```

## 📝 Keyingi Qadamlar

1. ✅ UX features - Tayyor
2. ✅ Static files - Tayyor
3. ⏳ SEO optimization
4. ⏳ Performance optimization
5. ⏳ Analytics integration

---

**Muallif:** Claude Code  
**Sana:** 2026-04-24  
**Versiya:** 1.0.0
