"""
Add all missing translations to .po files for uz, ru, en.
"""
import polib
import os

# All missing translations with their uz/ru/en values
TRANSLATIONS = {
    # --- Admin Panel ---
    'Accept Rules to Start Writing': {
        'uz': "Yozishni boshlash uchun qoidalarni qabul qiling",
        'ru': "Примите правила, чтобы начать писать",
        'en': "Accept Rules to Start Writing",
    },
    'Action': {
        'uz': "Amal",
        'ru': "Действие",
        'en': "Action",
    },
    'Action performed on {} articles.': {
        'uz': "{} ta maqolaga amal bajarildi.",
        'ru': "Действие выполнено для {} статей.",
        'en': "Action performed on {} articles.",
    },
    'Active Reviewers': {
        'uz': "Faol taqrizchilar",
        'ru': "Активные рецензенты",
        'en': "Active Reviewers",
    },
    'Active Users': {
        'uz': "Faol foydalanuvchilar",
        'ru': "Активные пользователи",
        'en': "Active Users",
    },
    'Add': {
        'uz': "Qo'shish",
        'ru': "Добавить",
        'en': "Add",
    },
    'Add New Reviewer': {
        'uz': "Yangi taqrizchi qo'shish",
        'ru': "Добавить нового рецензента",
        'en': "Add New Reviewer",
    },
    'Add your review comments here...': {
        'uz': "Taqriz izohlaringizni shu yerga yozing...",
        'ru': "Добавьте ваши комментарии к рецензии здесь...",
        'en': "Add your review comments here...",
    },
    'Additional Info': {
        'uz': "Qo'shimcha ma'lumot",
        'ru': "Дополнительная информация",
        'en': "Additional Info",
    },
    'Admin Account': {
        'uz': "Admin hisobi",
        'ru': "Аккаунт администратора",
        'en': "Admin Account",
    },
    'Admin Control Panel': {
        'uz': "Admin boshqaruv paneli",
        'ru': "Панель управления администратора",
        'en': "Admin Control Panel",
    },
    'Admin Dashboard': {
        'uz': "Admin boshqaruv paneli",
        'ru': "Панель администратора",
        'en': "Admin Dashboard",
    },
    'Admin Decision': {
        'uz': "Admin qarori",
        'ru': "Решение администратора",
        'en': "Admin Decision",
    },
    'Admin Panel': {
        'uz': "Admin panel",
        'ru': "Админ панель",
        'en': "Admin Panel",
    },
    'Administrators': {
        'uz': "Administratorlar",
        'ru': "Администраторы",
        'en': "Administrators",
    },
    'All Articles': {
        'uz': "Barcha maqolalar",
        'ru': "Все статьи",
        'en': "All Articles",
    },
    'All Status': {
        'uz': "Barcha holatlar",
        'ru': "Все статусы",
        'en': "All Status",
    },
    'All notifications marked as read.': {
        'uz': "Barcha bildirishnomalar o'qilgan deb belgilandi.",
        'ru': "Все уведомления отмечены как прочитанные.",
        'en': "All notifications marked as read.",
    },
    'All rights reserved.': {
        'uz': "Barcha huquqlar himoyalangan.",
        'ru': "Все права защищены.",
        'en': "All rights reserved.",
    },
    'Allowed file types: %(types)s': {
        'uz': "Ruxsat berilgan fayl turlari: %(types)s",
        'ru': "Допустимые типы файлов: %(types)s",
        'en': "Allowed file types: %(types)s",
    },
    'Allowed formats: PDF, DOC, DOCX. Maximum size: 20 MB.': {
        'uz': "Ruxsat berilgan formatlar: PDF, DOC, DOCX. Maksimal hajm: 20 MB.",
        'ru': "Допустимые форматы: PDF, DOC, DOCX. Максимальный размер: 20 МБ.",
        'en': "Allowed formats: PDF, DOC, DOCX. Maximum size: 20 MB.",
    },
    'Apply': {
        'uz': "Qo'llash",
        'ru': "Применить",
        'en': "Apply",
    },
    'Apply Action': {
        'uz': "Amalni qo'llash",
        'ru': "Применить действие",
        'en': "Apply Action",
    },
    'Apply Action to All': {
        'uz': "Hammasiga amalni qo'llash",
        'ru': "Применить действие ко всем",
        'en': "Apply Action to All",
    },
    'Approval Requirements': {
        'uz': "Tasdiqlash talablari",
        'ru': "Требования для одобрения",
        'en': "Approval Requirements",
    },
    'Article "%(title)s" has been deleted successfully.': {
        'uz': '"%(title)s" maqolasi muvaffaqiyatli o\'chirildi.',
        'ru': 'Статья "%(title)s" успешно удалена.',
        'en': 'Article "%(title)s" has been deleted successfully.',
    },
    'Article Action': {
        'uz': "Maqola amali",
        'ru': "Действие со статьёй",
        'en': "Article Action",
    },
    'Article Information': {
        'uz': "Maqola ma'lumotlari",
        'ru': "Информация о статье",
        'en': "Article Information",
    },
    'Article Statistics': {
        'uz': "Maqola statistikasi",
        'ru': "Статистика статей",
        'en': "Article Statistics",
    },
    'Article Status Breakdown': {
        'uz': "Maqola holatlari taqsimoti",
        'ru': "Распределение статусов статей",
        'en': "Article Status Breakdown",
    },
    'Article Status Histories': {
        'uz': "Maqola holati tarixi",
        'ru': "История статусов статей",
        'en': "Article Status Histories",
    },
    'Article Status History': {
        'uz': "Maqola holati tarixi",
        'ru': "История статуса статьи",
        'en': "Article Status History",
    },
    'Article has been rejected': {
        'uz': "Maqola rad etildi",
        'ru': "Статья отклонена",
        'en': "Article has been rejected",
    },
    'Article not available for review.': {
        'uz': "Maqola ko'rib chiqish uchun mavjud emas.",
        'ru': "Статья недоступна для рецензирования.",
        'en': "Article not available for review.",
    },
    'Article status reset to In Review.': {
        'uz': "Maqola holati Ko'rib chiqilmoqda holatiga qaytarildi.",
        'ru': "Статус статьи сброшен на «На рассмотрении».",
        'en': "Article status reset to In Review.",
    },
    'Article writing guidelines (text format)': {
        'uz': "Maqola yozish qoidalari (matn formati)",
        'ru': "Правила написания статей (текстовый формат)",
        'en': "Article writing guidelines (text format)",
    },
    'Articles Assigned': {
        'uz': "Tayinlangan maqolalar",
        'ru': "Назначенные статьи",
        'en': "Articles Assigned",
    },
    'Articles Waiting for Review': {
        'uz': "Ko'rib chiqishni kutayotgan maqolalar",
        'ru': "Статьи, ожидающие рецензирования",
        'en': "Articles Waiting for Review",
    },
    'Articles by Status': {
        'uz': "Maqolalar holat bo'yicha",
        'ru': "Статьи по статусу",
        'en': "Articles by Status",
    },
    'Assign categories for reviewers. Only relevant for users with Reviewer role.': {
        'uz': "Taqrizchilar uchun kategoriyalar tayinlang. Faqat Taqrizchi rolidagi foydalanuvchilar uchun.",
        'ru': "Назначьте категории для рецензентов. Только для пользователей с ролью «Рецензент».",
        'en': "Assign categories for reviewers. Only relevant for users with Reviewer role.",
    },
    'Assign reviewers who can review articles in this category': {
        'uz': "Ushbu kategoriyada maqolalarni ko'rib chiqishi mumkin bo'lgan taqrizchilarni tayinlang",
        'ru': "Назначьте рецензентов для рецензирования статей в этой категории",
        'en': "Assign reviewers who can review articles in this category",
    },
    'Assigned': {
        'uz': "Tayinlangan",
        'ru': "Назначено",
        'en': "Assigned",
    },
    'Assigned Categories': {
        'uz': "Tayinlangan kategoriyalar",
        'ru': "Назначенные категории",
        'en': "Assigned Categories",
    },
    'Assignment Details': {
        'uz': "Tayinlov tafsilotlari",
        'ru': "Детали назначения",
        'en': "Assignment Details",
    },
    'Attached File:': {
        'uz': "Biriktirma fayl:",
        'ru': "Прикреплённый файл:",
        'en': "Attached File:",
    },
    'Author:': {
        'uz': "Muallif:",
        'ru': "Автор:",
        'en': "Author:",
    },
    'Authors': {
        'uz': "Mualliflar",
        'ru': "Авторы",
        'en': "Authors",
    },
    'Back to All Articles': {
        'uz': "Barcha maqolalarga qaytish",
        'ru': "Вернуться ко всем статьям",
        'en': "Back to All Articles",
    },
    'Biography:': {
        'uz': "Biografiya:",
        'ru': "Биография:",
        'en': "Biography:",
    },
    'Built with': {
        'uz': "Yaratildi",
        'ru': "Создано с",
        'en': "Built with",
    },
    'Bulk Article Action': {
        'uz': "Ommaviy maqola amali",
        'ru': "Массовое действие со статьями",
        'en': "Bulk Article Action",
    },
    'By': {
        'uz': "Muallif",
        'ru': "От",
        'en': "By",
    },
    'Categories this reviewer can review. Only applies to users with Reviewer role.': {
        'uz': "Bu taqrizchi ko'rib chiqishi mumkin bo'lgan kategoriyalar. Faqat Taqrizchi rolidagi foydalanuvchilar uchun.",
        'ru': "Категории, которые может рецензировать этот рецензент. Только для пользователей с ролью «Рецензент».",
        'en': "Categories this reviewer can review. Only applies to users with Reviewer role.",
    },
    'Change request sent to author.': {
        'uz': "O'zgartirish so'rovi muallifga yuborildi.",
        'ru': "Запрос на изменения отправлен автору.",
        'en': "Change request sent to author.",
    },
    'Change selected users to Admin': {
        'uz': "Tanlangan foydalanuvchilarni Admin qilish",
        'ru': "Сделать выбранных пользователей администраторами",
        'en': "Change selected users to Admin",
    },
    'Change selected users to Author': {
        'uz': "Tanlangan foydalanuvchilarni Muallif qilish",
        'ru': "Сделать выбранных пользователей авторами",
        'en': "Change selected users to Author",
    },
    'Change selected users to Reader': {
        'uz': "Tanlangan foydalanuvchilarni O'quvchi qilish",
        'ru': "Сделать выбранных пользователей читателями",
        'en': "Change selected users to Reader",
    },
    'Changed By': {
        'uz': "O'zgartirgan",
        'ru': "Изменено",
        'en': "Changed By",
    },
    'Changes': {
        'uz': "O'zgartirishlar",
        'ru': "Изменения",
        'en': "Changes",
    },
    'Changes have been requested': {
        'uz': "O'zgartirishlar so'raldi",
        'ru': "Запрошены изменения",
        'en': "Changes have been requested",
    },
    'Classification': {
        'uz': "Tasnif",
        'ru': "Классификация",
        'en': "Classification",
    },
    'Confirm password': {
        'uz': "Parolni tasdiqlang",
        'ru': "Подтвердите пароль",
        'en': "Confirm password",
    },
    'Content Preview': {
        'uz': "Kontent ko'rinishi",
        'ru': "Предварительный просмотр содержания",
        'en': "Content Preview",
    },
    'Content cannot be empty.': {
        'uz': "Kontent bo'sh bo'lishi mumkin emas.",
        'ru': "Содержание не может быть пустым.",
        'en': "Content cannot be empty.",
    },
    'Create': {
        'uz': "Yaratish",
        'ru': "Создать",
        'en': "Create",
    },
    'Create New Reviewer': {
        'uz': "Yangi taqrizchi yaratish",
        'ru': "Создать нового рецензента",
        'en': "Create New Reviewer",
    },
    'Created:': {
        'uz': "Yaratilgan:",
        'ru': "Создано:",
        'en': "Created:",
    },
    'Date': {
        'uz': "Sana",
        'ru': "Дата",
        'en': "Date",
    },
    'Deadline': {
        'uz': "Muddat",
        'ru': "Срок",
        'en': "Deadline",
    },
    'Deadline by which the reviewer should complete the review': {
        'uz': "Taqrizchi ko'rib chiqishni yakunlashi kerak bo'lgan muddat",
        'ru': "Срок, до которого рецензент должен завершить рецензирование",
        'en': "Deadline by which the reviewer should complete the review",
    },
    'Delete Reviewer': {
        'uz': "Taqrizchini o'chirish",
        'ru': "Удалить рецензента",
        'en': "Delete Reviewer",
    },
    'Delete reviewer': {
        'uz': "Taqrizchini o'chirish",
        'ru': "Удалить рецензента",
        'en': "Delete reviewer",
    },
    'Details': {
        'uz': "Tafsilotlar",
        'ru': "Подробности",
        'en': "Details",
    },
    'Download PDF/Document': {
        'uz': "PDF/Hujjatni yuklab olish",
        'ru': "Скачать PDF/Документ",
        'en': "Download PDF/Document",
    },
    'E.g., 1, 2, 3...': {
        'uz': "Masalan, 1, 2, 3...",
        'ru': "Например, 1, 2, 3...",
        'en': "E.g., 1, 2, 3...",
    },
    'E.g., 2024': {
        'uz': "Masalan, 2024",
        'ru': "Например, 2024",
        'en': "E.g., 2024",
    },
    'Edit Article': {
        'uz': "Maqolani tahrirlash",
        'ru': "Редактировать статью",
        'en': "Edit Article",
    },
    'Edit Journal': {
        'uz': "Jurnalni tahrirlash",
        'ru': "Редактировать журнал",
        'en': "Edit Journal",
    },
    'Edit Reviewer': {
        'uz': "Taqrizchini tahrirlash",
        'ru': "Редактировать рецензента",
        'en': "Edit Reviewer",
    },
    'Edit reviewer': {
        'uz': "Taqrizchini tahrirlash",
        'ru': "Редактировать рецензента",
        'en': "Edit reviewer",
    },
    'Email address': {
        'uz': "Elektron pochta manzili",
        'ru': "Адрес электронной почты",
        'en': "Email address",
    },
    'Email:': {
        'uz': "Elektron pochta:",
        'ru': "Email:",
        'en': "Email:",
    },
    'Enter a keyword and press Add or Enter': {
        'uz': "Kalit so'zni kiriting va Qo'shish yoki Enter tugmasini bosing",
        'ru': "Введите ключевое слово и нажмите «Добавить» или Enter",
        'en': "Enter a keyword and press Add or Enter",
    },
    'Enter admin note (visible to author)': {
        'uz': "Admin izohini kiriting (muallifga ko'rinadi)",
        'ru': "Введите заметку администратора (видна автору)",
        'en': "Enter admin note (visible to author)",
    },
    'Enter password': {
        'uz': "Parolni kiriting",
        'ru': "Введите пароль",
        'en': "Enter password",
    },
    'Enter publication number (e.g., 1, 2, 3...)': {
        'uz': "Nashr raqamini kiriting (masalan, 1, 2, 3...)",
        'ru': "Введите номер выпуска (например, 1, 2, 3...)",
        'en': "Enter publication number (e.g., 1, 2, 3...)",
    },
    'Enter publication year (e.g., 2024)': {
        'uz': "Nashr yilini kiriting (masalan, 2024)",
        'ru': "Введите год публикации (например, 2024)",
        'en': "Enter publication year (e.g., 2024)",
    },
    'Enter title in English (optional)': {
        'uz': "Sarlavhani ingliz tilida kiriting (ixtiyoriy)",
        'ru': "Введите заголовок на английском (необязательно)",
        'en': "Enter title in English (optional)",
    },
    'Enter title in Russian (optional)': {
        'uz': "Sarlavhani rus tilida kiriting (ixtiyoriy)",
        'ru': "Введите заголовок на русском (необязательно)",
        'en': "Enter title in Russian (optional)",
    },
    'Enter title in Uzbek': {
        'uz': "Sarlavhani o'zbek tilida kiriting",
        'ru': "Введите заголовок на узбекском",
        'en': "Enter title in Uzbek",
    },
    'Feedback': {
        'uz': "Fikr-mulohaza",
        'ru': "Отзыв",
        'en': "Feedback",
    },
    'File size must not exceed %(size)s MB.': {
        'uz': "Fayl hajmi %(size)s MB dan oshmasligi kerak.",
        'ru': "Размер файла не должен превышать %(size)s МБ.",
        'en': "File size must not exceed %(size)s MB.",
    },
    'Filter': {
        'uz': "Filtrlash",
        'ru': "Фильтр",
        'en': "Filter",
    },
    'First': {
        'uz': "Birinchi",
        'ru': "Первая",
        'en': "First",
    },
    'First name': {
        'uz': "Ism",
        'ru': "Имя",
        'en': "First name",
    },
    'From Status': {
        'uz': "Oldingi holat",
        'ru': "Из статуса",
        'en': "From Status",
    },
    'Go to Admin Panel': {
        'uz': "Admin panelga o'tish",
        'ru': "Перейти в админ панель",
        'en': "Go to Admin Panel",
    },
    'Go to Review Page': {
        'uz': "Ko'rib chiqish sahifasiga o'tish",
        'ru': "Перейти на страницу рецензирования",
        'en': "Go to Review Page",
    },
    'Go to Reviewer Dashboard': {
        'uz': "Taqrizchi paneliga o'tish",
        'ru': "Перейти в панель рецензента",
        'en': "Go to Reviewer Dashboard",
    },
    'Inactive': {
        'uz': "Nofaol",
        'ru': "Неактивен",
        'en': "Inactive",
    },
    'Information': {
        'uz': "Ma'lumot",
        'ru': "Информация",
        'en': "Information",
    },
    'Invalid keyword data.': {
        'uz': "Noto'g'ri kalit so'z ma'lumoti.",
        'ru': "Неверные данные ключевого слова.",
        'en': "Invalid keyword data.",
    },
    'Journal Information': {
        'uz': "Jurnal ma'lumotlari",
        'ru': "Информация о журнале",
        'en': "Journal Information",
    },
    'Journal created successfully.': {
        'uz': "Jurnal muvaffaqiyatli yaratildi.",
        'ru': "Журнал успешно создан.",
        'en': "Journal created successfully.",
    },
    'Journal deactivated.': {
        'uz': "Jurnal o'chirildi.",
        'ru': "Журнал деактивирован.",
        'en': "Journal deactivated.",
    },
    'Journal updated successfully.': {
        'uz': "Jurnal muvaffaqiyatli yangilandi.",
        'ru': "Журнал успешно обновлён.",
        'en': "Journal updated successfully.",
    },
    'Keyword is too long (max 100 characters).': {
        'uz': "Kalit so'z juda uzun (maksimum 100 belgi).",
        'ru': "Ключевое слово слишком длинное (максимум 100 символов).",
        'en': "Keyword is too long (max 100 characters).",
    },
    'Last': {
        'uz': "Oxirgi",
        'ru': "Последняя",
        'en': "Last",
    },
    'Last Modified:': {
        'uz': "Oxirgi o'zgartirilgan:",
        'ru': "Последнее изменение:",
        'en': "Last Modified:",
    },
    'Last name': {
        'uz': "Familiya",
        'ru': "Фамилия",
        'en': "Last name",
    },
    'Link': {
        'uz': "Havola",
        'ru': "Ссылка",
        'en': "Link",
    },
    'Make Reviewer and Send Notification': {
        'uz': "Taqrizchi qilib tayinlash va bildirishnoma yuborish",
        'ru': "Назначить рецензентом и отправить уведомление",
        'en': "Make Reviewer and Send Notification",
    },
    'Manage Articles': {
        'uz': "Maqolalarni boshqarish",
        'ru': "Управление статьями",
        'en': "Manage Articles",
    },
    'Manage Reviewers': {
        'uz': "Taqrizchilarni boshqarish",
        'ru': "Управление рецензентами",
        'en': "Manage Reviewers",
    },
    'Manage your assigned article reviews': {
        'uz': "Sizga tayinlangan maqola taqrizlarini boshqaring",
        'ru': "Управляйте назначенными вам рецензиями статей",
        'en': "Manage your assigned article reviews",
    },
    'Mark All as Read': {
        'uz': "Hammasini o'qilgan deb belgilash",
        'ru': "Отметить всё как прочитанное",
        'en': "Mark All as Read",
    },
    'Mark Read': {
        'uz': "O'qilgan",
        'ru': "Прочитано",
        'en': "Mark Read",
    },
    'Mark selected as read': {
        'uz': "Tanlanganlarni o'qilgan deb belgilash",
        'ru': "Отметить выбранные как прочитанные",
        'en': "Mark selected as read",
    },
    'Mark selected as unread': {
        'uz': "Tanlanganlarni o'qilmagan deb belgilash",
        'ru': "Отметить выбранные как непрочитанные",
        'en': "Mark selected as unread",
    },
    'Message': {
        'uz': "Xabar",
        'ru': "Сообщение",
        'en': "Message",
    },
    'Name': {
        'uz': "Nomi",
        'ru': "Имя",
        'en': "Name",
    },
    'Names (Multilingual)': {
        'uz': "Nomlar (Ko'p tilli)",
        'ru': "Названия (Многоязычные)",
        'en': "Names (Multilingual)",
    },
    'New': {
        'uz': "Yangi",
        'ru': "Новое",
        'en': "New",
    },
    'No': {
        'uz': "Yo'q",
        'ru': "Нет",
        'en': "No",
    },
    'No articles assigned from any journal.': {
        'uz': "Hech qanday jurnaldan maqola tayinlanmagan.",
        'ru': "Нет назначенных статей из журналов.",
        'en': "No articles assigned from any journal.",
    },
    'No articles found.': {
        'uz': "Maqolalar topilmadi.",
        'ru': "Статьи не найдены.",
        'en': "No articles found.",
    },
    'No articles in this category yet.': {
        'uz': "Bu kategoriyada hali maqola yo'q.",
        'ru': "В этой категории пока нет статей.",
        'en': "No articles in this category yet.",
    },
    'No articles selected.': {
        'uz': "Maqola tanlanmagan.",
        'ru': "Статьи не выбраны.",
        'en': "No articles selected.",
    },
    'No articles yet. Create your first article!': {
        'uz': "Hali maqola yo'q. Birinchi maqolangizni yarating!",
        'ru': "Статей пока нет. Создайте свою первую статью!",
        'en': "No articles yet. Create your first article!",
    },
    'No pending articles to review.': {
        'uz': "Ko'rib chiqish uchun kutilayotgan maqola yo'q.",
        'ru': "Нет статей, ожидающих рецензирования.",
        'en': "No pending articles to review.",
    },
    'No pending articles. Great job!': {
        'uz': "Kutayotgan maqola yo'q. Ajoyib!",
        'ru': "Нет ожидающих статей. Отличная работа!",
        'en': "No pending articles. Great job!",
    },
    'No pending reviewer assignments': {
        'uz': "Kutayotgan taqrizchi tayinlovlari yo'q",
        'ru': "Нет ожидающих назначений рецензентов",
        'en': "No pending reviewer assignments",
    },
    'No published articles yet.': {
        'uz': "Hali nashr qilingan maqola yo'q.",
        'ru': "Пока нет опубликованных статей.",
        'en': "No published articles yet.",
    },
    'No reviewers found.': {
        'uz': "Taqrizchilar topilmadi.",
        'ru': "Рецензенты не найдены.",
        'en': "No reviewers found.",
    },
    'No reviews received yet.': {
        'uz': "Hali taqriz olinmagan.",
        'ru': "Рецензии ещё не получены.",
        'en': "No reviews received yet.",
    },
    'No reviews yet.': {
        'uz': "Hali taqrizlar yo'q.",
        'ru': "Рецензий пока нет.",
        'en': "No reviews yet.",
    },
    'No status changes recorded.': {
        'uz': "Holat o'zgarishlari qayd etilmagan.",
        'ru': "Изменения статуса не зарегистрированы.",
        'en': "No status changes recorded.",
    },
    'Not submitted': {
        'uz': "Yuborilmagan",
        'ru': "Не отправлено",
        'en': "Not submitted",
    },
    'Note (for rejection/changes)': {
        'uz': "Izoh (rad etish/o'zgartirish uchun)",
        'ru': "Заметка (для отклонения/изменений)",
        'en': "Note (for rejection/changes)",
    },
    'Notification': {
        'uz': "Bildirishnoma",
        'ru': "Уведомление",
        'en': "Notification",
    },
    'Only .txt files are allowed for rules.': {
        'uz': "Qoidalar uchun faqat .txt fayllar ruxsat etiladi.",
        'ru': "Для правил допускаются только файлы .txt.",
        'en': "Only .txt files are allowed for rules.",
    },
    'Optional: Publication issue number': {
        'uz': "Ixtiyoriy: Nashr raqami",
        'ru': "Необязательно: Номер выпуска",
        'en': "Optional: Publication issue number",
    },
    'Optional: Year the article was published': {
        'uz': "Ixtiyoriy: Maqola nashr etilgan yil",
        'ru': "Необязательно: Год публикации статьи",
        'en': "Optional: Year the article was published",
    },
    'Options': {
        'uz': "Amallar",
        'ru': "Опции",
        'en': "Options",
    },
    'Organization:': {
        'uz': "Tashkilot:",
        'ru': "Организация:",
        'en': "Organization:",
    },
    'Overview': {
        'uz': "Umumiy ko'rinish",
        'ru': "Обзор",
        'en': "Overview",
    },
    'Passwords do not match.': {
        'uz': "Parollar mos kelmadi.",
        'ru': "Пароли не совпадают.",
        'en': "Passwords do not match.",
    },
    'Pending Admin': {
        'uz': "Admin kutmoqda",
        'ru': "Ожидает администратора",
        'en': "Pending Admin",
    },
    'Pending Articles': {
        'uz': "Kutayotgan maqolalar",
        'ru': "Ожидающие статьи",
        'en': "Pending Articles",
    },
    'Pending Reviews': {
        'uz': "Kutayotgan taqrizlar",
        'ru': "Ожидающие рецензии",
        'en': "Pending Reviews",
    },
    'Perform Action': {
        'uz': "Amalni bajarish",
        'ru': "Выполнить действие",
        'en': "Perform Action",
    },
    'Please add at least one keyword.': {
        'uz': "Iltimos, kamida bitta kalit so'z qo'shing.",
        'ru': "Пожалуйста, добавьте хотя бы одно ключевое слово.",
        'en': "Please add at least one keyword.",
    },
    'Please provide a comment explaining the reason for rejection.': {
        'uz': "Iltimos, rad etish sababini tushuntirib izoh yozing.",
        'ru': "Пожалуйста, напишите комментарий с объяснением причины отклонения.",
        'en': "Please provide a comment explaining the reason for rejection.",
    },
    'Please provide a comment explaining what changes are needed.': {
        'uz': "Iltimos, qanday o'zgartirishlar kerakligini tushuntirib izoh yozing.",
        'ru': "Пожалуйста, напишите комментарий с объяснением необходимых изменений.",
        'en': "Please provide a comment explaining what changes are needed.",
    },
    'Please provide constructive feedback for the author.': {
        'uz': "Iltimos, muallif uchun konstruktiv fikr-mulohaza bering.",
        'ru': "Пожалуйста, предоставьте конструктивный отзыв для автора.",
        'en': "Please provide constructive feedback for the author.",
    },
    'Please review the feedback and make necessary changes.': {
        'uz': "Iltimos, fikr-mulohazani ko'rib chiqing va kerakli o'zgartirishlarni kiriting.",
        'ru': "Пожалуйста, ознакомьтесь с отзывом и внесите необходимые изменения.",
        'en': "Please review the feedback and make necessary changes.",
    },
    'Please review your article and make necessary improvements before resubmitting.': {
        'uz': "Iltimos, maqolangizni ko'rib chiqing va qayta yuborishdan oldin kerakli yaxshilanishlarni kiriting.",
        'ru': "Пожалуйста, просмотрите свою статью и внесите необходимые улучшения перед повторной отправкой.",
        'en': "Please review your article and make necessary improvements before resubmitting.",
    },
    'Professional Review Process': {
        'uz': "Professional ko'rib chiqish jarayoni",
        'ru': "Профессиональный процесс рецензирования",
        'en': "Professional Review Process",
    },
    'Professional article publishing platform for quality content.': {
        'uz': "Sifatli kontent uchun professional maqola nashr etish platformasi.",
        'ru': "Профессиональная платформа для публикации качественных статей.",
        'en': "Professional article publishing platform for quality content.",
    },
    'Publication Info': {
        'uz': "Nashr ma'lumotlari",
        'ru': "Информация о публикации",
        'en': "Publication Info",
    },
    'Publication Number': {
        'uz': "Nashr raqami",
        'ru': "Номер выпуска",
        'en': "Publication Number",
    },
    'Publication Year': {
        'uz': "Nashr yili",
        'ru': "Год публикации",
        'en': "Publication Year",
    },
    'Publication year (e.g., 2026)': {
        'uz': "Nashr yili (masalan, 2026)",
        'ru': "Год публикации (например, 2026)",
        'en': "Publication year (e.g., 2026)",
    },
    'Publish Article': {
        'uz': "Maqolani nashr qilish",
        'ru': "Опубликовать статью",
        'en': "Publish Article",
    },
    'Publish Selected': {
        'uz': "Tanlanganlarni nashr qilish",
        'ru': "Опубликовать выбранные",
        'en': "Publish Selected",
    },
    'Publishable': {
        'uz': "Nashr qilish mumkin",
        'ru': "Готова к публикации",
        'en': "Publishable",
    },
    'Publishing Quality Content': {
        'uz': "Sifatli kontent nashr qilish",
        'ru': "Публикация качественного контента",
        'en': "Publishing Quality Content",
    },
    'Publishing Status': {
        'uz': "Nashr holati",
        'ru': "Статус публикации",
        'en': "Publishing Status",
    },
    'Quick Links': {
        'uz': "Tezkor havolalar",
        'ru': "Быстрые ссылки",
        'en': "Quick Links",
    },
    'Read More': {
        'uz': "Batafsil o'qish",
        'ru': "Читать далее",
        'en': "Read More",
    },
    'Readers': {
        'uz': "O'quvchilar",
        'ru': "Читатели",
        'en': "Readers",
    },
    'Recent Notifications': {
        'uz': "So'nggi bildirishnomalar",
        'ru': "Последние уведомления",
        'en': "Recent Notifications",
    },
    'Recent Published Articles': {
        'uz': "So'nggi nashr qilingan maqolalar",
        'ru': "Последние опубликованные статьи",
        'en': "Recent Published Articles",
    },
    'Recent Reviews': {
        'uz': "So'nggi taqrizlar",
        'ru': "Последние рецензии",
        'en': "Recent Reviews",
    },
    'Recent Reviews Received': {
        'uz': "So'nggi olingan taqrizlar",
        'ru': "Последние полученные рецензии",
        'en': "Recent Reviews Received",
    },
    'Reject Article': {
        'uz': "Maqolani rad etish",
        'ru': "Отклонить статью",
        'en': "Reject Article",
    },
    'Reject Selected': {
        'uz': "Tanlanganlarni rad etish",
        'ru': "Отклонить выбранные",
        'en': "Reject Selected",
    },
    'Request Changes on Selected': {
        'uz': "Tanlanganlarga o'zgartirish so'rash",
        'ru': "Запросить изменения для выбранных",
        'en': "Request Changes on Selected",
    },
    'Reset to In Review': {
        'uz': "Ko'rib chiqish holatiga qaytarish",
        'ru': "Сбросить на «На рассмотрении»",
        'en': "Reset to In Review",
    },
    'Review Article': {
        'uz': "Maqolani ko'rib chiqish",
        'ru': "Рецензировать статью",
        'en': "Review Article",
    },
    'Review Deadline': {
        'uz': "Ko'rib chiqish muddati",
        'ru': "Срок рецензирования",
        'en': "Review Deadline",
    },
    'Review Details': {
        'uz': "Taqriz tafsilotlari",
        'ru': "Подробности рецензии",
        'en': "Review Details",
    },
    'Review Feedback': {
        'uz': "Taqriz fikr-mulohazasi",
        'ru': "Отзыв рецензента",
        'en': "Review Feedback",
    },
    'Review Queue': {
        'uz': "Ko'rib chiqish navbati",
        'ru': "Очередь рецензирования",
        'en': "Review Queue",
    },
    'Review Statistics': {
        'uz': "Taqriz statistikasi",
        'ru': "Статистика рецензий",
        'en': "Review Statistics",
    },
    'Review submitted for your article': {
        'uz': "Maqolangiz uchun taqriz yuborildi",
        'ru': "Рецензия отправлена для вашей статьи",
        'en': "Review submitted for your article",
    },
    'Reviewed': {
        'uz': "Ko'rib chiqilgan",
        'ru': "Рецензировано",
        'en': "Reviewed",
    },
    'Reviewer Categories': {
        'uz': "Taqrizchi kategoriyalari",
        'ru': "Категории рецензента",
        'en': "Reviewer Categories",
    },
    'Reviewer Information': {
        'uz': "Taqrizchi ma'lumotlari",
        'ru': "Информация о рецензенте",
        'en': "Reviewer Information",
    },
    'Reviewer created successfully.': {
        'uz': "Taqrizchi muvaffaqiyatli yaratildi.",
        'ru': "Рецензент успешно создан.",
        'en': "Reviewer created successfully.",
    },
    'Reviewer deleted successfully.': {
        'uz': "Taqrizchi muvaffaqiyatli o'chirildi.",
        'ru': "Рецензент успешно удалён.",
        'en': "Reviewer deleted successfully.",
    },
    'Reviewer updated successfully.': {
        'uz': "Taqrizchi muvaffaqiyatli yangilandi.",
        'ru': "Рецензент успешно обновлён.",
        'en': "Reviewer updated successfully.",
    },
    'Reviewers': {
        'uz': "Taqrizchilar",
        'ru': "Рецензенты",
        'en': "Reviewers",
    },
    'Reviews by Decision': {
        'uz': "Qaror bo'yicha taqrizlar",
        'ru': "Рецензии по решению",
        'en': "Reviews by Decision",
    },
    'Role & Profile': {
        'uz': "Rol va profil",
        'ru': "Роль и профиль",
        'en': "Role & Profile",
    },
    'Rules File': {
        'uz': "Qoidalar fayli",
        'ru': "Файл правил",
        'en': "Rules File",
    },
    'Rules file size cannot exceed 5MB.': {
        'uz': "Qoidalar fayli hajmi 5MB dan oshmasligi kerak.",
        'ru': "Размер файла правил не должен превышать 5 МБ.",
        'en': "Rules file size cannot exceed 5MB.",
    },
    'Search by name, username, or email...': {
        'uz': "Ism, foydalanuvchi nomi yoki email bo'yicha qidiring...",
        'ru': "Поиск по имени, логину или email...",
        'en': "Search by name, username, or email...",
    },
    'Search by title, content, keywords...': {
        'uz': "Sarlavha, mazmun, kalit so'zlar bo'yicha qidiring...",
        'ru': "Поиск по заголовку, содержанию, ключевым словам...",
        'en': "Search by title, content, keywords...",
    },
    'Secure & Scalable': {
        'uz': "Xavfsiz va kengaytiriluvchan",
        'ru': "Безопасно и масштабируемо",
        'en': "Secure & Scalable",
    },
    'Select bulk action...': {
        'uz': "Ommaviy amalni tanlang...",
        'ru': "Выберите массовое действие...",
        'en': "Select bulk action...",
    },
    'Selected Articles': {
        'uz': "Tanlangan maqolalar",
        'ru': "Выбранные статьи",
        'en': "Selected Articles",
    },
    'Status Change': {
        'uz': "Holat o'zgarishi",
        'ru': "Изменение статуса",
        'en': "Status Change",
    },
    'Status History': {
        'uz': "Holat tarixi",
        'ru': "История статуса",
        'en': "Status History",
    },
    'Status:': {
        'uz': "Holat:",
        'ru': "Статус:",
        'en': "Status:",
    },
    'Submit Review': {
        'uz': "Taqrizni yuborish",
        'ru': "Отправить рецензию",
        'en': "Submit Review",
    },
    'Submit Your Review': {
        'uz': "Taqrizingizni yuboring",
        'ru': "Отправьте вашу рецензию",
        'en': "Submit Your Review",
    },
    'Submitted': {
        'uz': "Yuborilgan",
        'ru': "Отправлено",
        'en': "Submitted",
    },
    'Submitted:': {
        'uz': "Yuborilgan:",
        'ru': "Отправлено:",
        'en': "Submitted:",
    },
    'System': {
        'uz': "Tizim",
        'ru': "Система",
        'en': "System",
    },
    'System Statistics': {
        'uz': "Tizim statistikasi",
        'ru': "Системная статистика",
        'en': "System Statistics",
    },
    'System Statistics and Analytics': {
        'uz': "Tizim statistikasi va tahlili",
        'ru': "Системная статистика и аналитика",
        'en': "System Statistics and Analytics",
    },
    'Take Action': {
        'uz': "Amal bajarish",
        'ru': "Принять меры",
        'en': "Take Action",
    },
    'The category this review is for': {
        'uz': "Ushbu taqriz tegishli bo'lgan kategoriya",
        'ru': "Категория, к которой относится эта рецензия",
        'en': "The category this review is for",
    },
    'This action cannot be undone. All review assignments will be removed.': {
        'uz': "Bu amalni bekor qilib bo'lmaydi. Barcha taqriz tayinlovlari o'chiriladi.",
        'ru': "Это действие нельзя отменить. Все назначения рецензий будут удалены.",
        'en': "This action cannot be undone. All review assignments will be removed.",
    },
    'This article cannot be edited in its current status.': {
        'uz': "Bu maqolani joriy holatda tahrirlash mumkin emas.",
        'ru': "Эту статью нельзя редактировать в текущем статусе.",
        'en': "This article cannot be edited in its current status.",
    },
    'This note will be visible to the author': {
        'uz': "Bu izoh muallifga ko'rinadi",
        'ru': "Эта заметка будет видна автору",
        'en': "This note will be visible to the author",
    },
    'Timestamp': {
        'uz': "Vaqt",
        'ru': "Время",
        'en': "Timestamp",
    },
    'Title (English):': {
        'uz': "Sarlavha (inglizcha):",
        'ru': "Заголовок (английский):",
        'en': "Title (English):",
    },
    'Title (Russian):': {
        'uz': "Sarlavha (ruscha):",
        'ru': "Заголовок (русский):",
        'en': "Title (Russian):",
    },
    'Title (Uzbek):': {
        'uz': "Sarlavha (o'zbekcha):",
        'ru': "Заголовок (узбекский):",
        'en': "Title (Uzbek):",
    },
    'Title cannot be empty.': {
        'uz': "Sarlavha bo'sh bo'lishi mumkin emas.",
        'ru': "Заголовок не может быть пустым.",
        'en': "Title cannot be empty.",
    },
    'Title cannot exceed 300 characters.': {
        'uz': "Sarlavha 300 belgidan oshmasligi kerak.",
        'ru': "Заголовок не должен превышать 300 символов.",
        'en': "Title cannot exceed 300 characters.",
    },
    'To Status': {
        'uz': "Yangi holat",
        'ru': "В статус",
        'en': "To Status",
    },
    'Top Reviewers': {
        'uz': "Eng yaxshi taqrizchilar",
        'ru': "Лучшие рецензенты",
        'en': "Top Reviewers",
    },
    'Total Reviews': {
        'uz': "Jami taqrizlar",
        'ru': "Всего рецензий",
        'en': "Total Reviews",
    },
    'Total Users': {
        'uz': "Jami foydalanuvchilar",
        'ru': "Всего пользователей",
        'en': "Total Users",
    },
    'Total selected:': {
        'uz': "Jami tanlangan:",
        'ru': "Всего выбрано:",
        'en': "Total selected:",
    },
    "Type a keyword and click Add (or press Enter). You can add as many as you want.": {
        'uz': "Kalit so'zni yozing va Qo'shish tugmasini bosing (yoki Enter). Xohlaganingizcha qo'shishingiz mumkin.",
        'ru': "Введите ключевое слово и нажмите «Добавить» (или Enter). Можно добавить сколько угодно.",
        'en': "Type a keyword and click Add (or press Enter). You can add as many as you want.",
    },
    'Updated': {
        'uz': "Yangilangan",
        'ru': "Обновлено",
        'en': "Updated",
    },
    'Upload rules as .txt file (optional, max 5MB)': {
        'uz': ".txt fayl sifatida qoidalarni yuklang (ixtiyoriy, maks 5MB)",
        'ru': "Загрузите правила в формате .txt (необязательно, макс. 5 МБ)",
        'en': "Upload rules as .txt file (optional, max 5MB)",
    },
    'Use this for rejection or change requests (optional)': {
        'uz': "Buni rad etish yoki o'zgartirish so'rovi uchun ishlating (ixtiyoriy)",
        'ru': "Используйте для отклонения или запроса на изменения (необязательно)",
        'en': "Use this for rejection or change requests (optional)",
    },
    'User Management Statistics': {
        'uz': "Foydalanuvchilarni boshqarish statistikasi",
        'ru': "Статистика управления пользователями",
        'en': "User Management Statistics",
    },
    'Username:': {
        'uz': "Foydalanuvchi nomi:",
        'ru': "Имя пользователя:",
        'en': "Username:",
    },
    'Users by Role': {
        'uz': "Foydalanuvchilar rol bo'yicha",
        'ru': "Пользователи по ролям",
        'en': "Users by Role",
    },
    'View All': {
        'uz': "Hammasini ko'rish",
        'ru': "Посмотреть все",
        'en': "View All",
    },
    'View Article': {
        'uz': "Maqolani ko'rish",
        'ru': "Просмотреть статью",
        'en': "View Article",
    },
    'View Full Article': {
        'uz': "To'liq maqolani ko'rish",
        'ru': "Просмотреть полную статью",
        'en': "View Full Article",
    },
    'View details': {
        'uz': "Tafsilotlarni ko'rish",
        'ru': "Подробнее",
        'en': "View details",
    },
    'Waiting for reviewer approval': {
        'uz': "Taqrizchi tasdig'ini kutmoqda",
        'ru': "Ожидает одобрения рецензента",
        'en': "Waiting for reviewer approval",
    },
    'Waiting for reviewer submissions': {
        'uz': "Taqrizchi javoblarini kutmoqda",
        'ru': "Ожидает ответов рецензентов",
        'en': "Waiting for reviewer submissions",
    },
    'Write article content in English (optional)': {
        'uz': "Maqola mazmunini ingliz tilida yozing (ixtiyoriy)",
        'ru': "Напишите содержание статьи на английском (необязательно)",
        'en': "Write article content in English (optional)",
    },
    'Write article content in Russian (optional)': {
        'uz': "Maqola mazmunini rus tilida yozing (ixtiyoriy)",
        'ru': "Напишите содержание статьи на русском (необязательно)",
        'en': "Write article content in Russian (optional)",
    },
    'Write article content in Uzbek': {
        'uz': "Maqola mazmunini o'zbek tilida yozing",
        'ru': "Напишите содержание статьи на узбекском",
        'en': "Write article content in Uzbek",
    },
    'Write your review comments...': {
        'uz': "Taqriz izohlaringizni yozing...",
        'ru': "Напишите ваши комментарии к рецензии...",
        'en': "Write your review comments...",
    },
    'Yes': {
        'uz': "Ha",
        'ru': "Да",
        'en': "Yes",
    },
    'Yes, Delete This Reviewer': {
        'uz': "Ha, bu taqrizchini o'chirish",
        'ru': "Да, удалить этого рецензента",
        'en': "Yes, Delete This Reviewer",
    },
    'You are about to delete the reviewer:': {
        'uz': "Siz quyidagi taqrizchini o'chirmoqchisiz:",
        'ru': "Вы собираетесь удалить рецензента:",
        'en': "You are about to delete the reviewer:",
    },
    'You are not assigned to review this article.': {
        'uz': "Sizga bu maqolani ko'rib chiqish tayinlanmagan.",
        'ru': "Вам не назначено рецензирование этой статьи.",
        'en': "You are not assigned to review this article.",
    },
    'You can review this article for the following categories:': {
        'uz': "Siz bu maqolani quyidagi kategoriyalar uchun ko'rib chiqishingiz mumkin:",
        'ru': "Вы можете рецензировать эту статью по следующим категориям:",
        'en': "You can review this article for the following categories:",
    },
    'You do not have permission to access the admin panel.': {
        'uz': "Sizda admin panelga kirish huquqi yo'q.",
        'ru': "У вас нет прав доступа к панели администратора.",
        'en': "You do not have permission to access the admin panel.",
    },
    "You don't have any notifications yet.": {
        'uz': "Sizda hali bildirishnomalar yo'q.",
        'ru': "У вас пока нет уведомлений.",
        'en': "You don't have any notifications yet.",
    },
    'You have already reviewed this article.': {
        'uz': "Siz bu maqolani allaqachon ko'rib chiqqansiz.",
        'ru': "Вы уже рецензировали эту статью.",
        'en': "You have already reviewed this article.",
    },
    'You have not reviewed any articles yet.': {
        'uz': "Siz hali hech qanday maqolani ko'rib chiqmagansiz.",
        'ru': "Вы ещё не рецензировали ни одной статьи.",
        'en': "You have not reviewed any articles yet.",
    },
    'Your Comment': {
        'uz': "Sizning izohingiz",
        'ru': "Ваш комментарий",
        'en': "Your Comment",
    },
    'Your Decision': {
        'uz': "Sizning qaroringiz",
        'ru': "Ваше решение",
        'en': "Your Decision",
    },
    'Your Feedback': {
        'uz': "Sizning fikr-mulohazangiz",
        'ru': "Ваш отзыв",
        'en': "Your Feedback",
    },
    'Your Recent Reviews': {
        'uz': "So'nggi taqrizlaringiz",
        'ru': "Ваши последние рецензии",
        'en': "Your Recent Reviews",
    },
    '[%(site_name)s] Article assigned for review: %(title)s': {
        'uz': "[%(site_name)s] Maqola ko'rib chiqish uchun tayinlandi: %(title)s",
        'ru': "[%(site_name)s] Статья назначена для рецензирования: %(title)s",
        'en': "[%(site_name)s] Article assigned for review: %(title)s",
    },
    '[%(site_name)s] Article published: %(title)s': {
        'uz': "[%(site_name)s] Maqola nashr qilindi: %(title)s",
        'ru': "[%(site_name)s] Статья опубликована: %(title)s",
        'en': "[%(site_name)s] Article published: %(title)s",
    },
    '[%(site_name)s] Article resubmitted: %(title)s': {
        'uz': "[%(site_name)s] Maqola qayta yuborildi: %(title)s",
        'ru': "[%(site_name)s] Статья отправлена повторно: %(title)s",
        'en': "[%(site_name)s] Article resubmitted: %(title)s",
    },
    '[%(site_name)s] Changes requested for your article: %(title)s': {
        'uz': "[%(site_name)s] Maqolangizga o'zgartirishlar so'raldi: %(title)s",
        'ru': "[%(site_name)s] Запрошены изменения для вашей статьи: %(title)s",
        'en': "[%(site_name)s] Changes requested for your article: %(title)s",
    },
    '[%(site_name)s] New article assigned for review: %(title)s': {
        'uz': "[%(site_name)s] Yangi maqola ko'rib chiqish uchun tayinlandi: %(title)s",
        'ru': "[%(site_name)s] Новая статья назначена для рецензирования: %(title)s",
        'en': "[%(site_name)s] New article assigned for review: %(title)s",
    },
    '[%(site_name)s] New article submitted: %(title)s': {
        'uz': "[%(site_name)s] Yangi maqola yuborildi: %(title)s",
        'ru': "[%(site_name)s] Новая статья отправлена: %(title)s",
        'en': "[%(site_name)s] New article submitted: %(title)s",
    },
    '[%(site_name)s] Review update for your article: %(title)s': {
        'uz': "[%(site_name)s] Maqolangiz uchun taqriz yangilandi: %(title)s",
        'ru': "[%(site_name)s] Обновление рецензии для вашей статьи: %(title)s",
        'en': "[%(site_name)s] Review update for your article: %(title)s",
    },
    '[%(site_name)s] You have been assigned as a Reviewer': {
        'uz': "[%(site_name)s] Siz taqrizchi sifatida tayinlandingiz",
        'ru': "[%(site_name)s] Вы назначены рецензентом",
        'en': "[%(site_name)s] You have been assigned as a Reviewer",
    },
    '[%(site_name)s] Your article has been published: %(title)s': {
        'uz': "[%(site_name)s] Maqolangiz nashr qilindi: %(title)s",
        'ru': "[%(site_name)s] Ваша статья опубликована: %(title)s",
        'en': "[%(site_name)s] Your article has been published: %(title)s",
    },
    '[%(site_name)s] Your article has been rejected: %(title)s': {
        'uz': "[%(site_name)s] Maqolangiz rad etildi: %(title)s",
        'ru': "[%(site_name)s] Ваша статья отклонена: %(title)s",
        'en': "[%(site_name)s] Your article has been rejected: %(title)s",
    },
    'ago': {
        'uz': "oldin",
        'ru': "назад",
        'en': "ago",
    },
    'assignment(s)': {
        'uz': "tayinlov(lar)",
        'ru': "назначение(я)",
        'en': "assignment(s)",
    },
    'minimum 1 required': {
        'uz': "kamida 1 ta talab qilinadi",
        'ru': "минимум 1 обязательно",
        'en': "minimum 1 required",
    },
    'pending': {
        'uz': "kutilmoqda",
        'ru': "ожидает",
        'en': "pending",
    },
    'unread notifications': {
        'uz': "o'qilmagan bildirishnomalar",
        'ru': "непрочитанные уведомления",
        'en': "unread notifications",
    },
    'using Django & Bootstrap': {
        'uz': "Django va Bootstrap yordamida",
        'ru': "с использованием Django и Bootstrap",
        'en': "using Django & Bootstrap",
    },

    # === EN-only strings (from Python code, already translated in uz/ru) ===
    ' Comment: %(comment)s': {
        'uz': " Izoh: %(comment)s",
        'ru': " Комментарий: %(comment)s",
        'en': " Comment: %(comment)s",
    },
    ' Feedback: %(reason)s': {
        'uz': " Fikr-mulohaza: %(reason)s",
        'ru': " Отзыв: %(reason)s",
        'en': " Feedback: %(reason)s",
    },
    ' Reason: %(reason)s': {
        'uz': " Sabab: %(reason)s",
        'ru': " Причина: %(reason)s",
        'en': " Reason: %(reason)s",
    },
    '%(count)d article(s) published.': {
        'uz': "%(count)d ta maqola nashr qilindi.",
        'ru': "%(count)d статья(и) опубликована(ы).",
        'en': "%(count)d article(s) published.",
    },
    '%(count)d article(s) rejected.': {
        'uz': "%(count)d ta maqola rad etildi.",
        'ru': "%(count)d статья(и) отклонена(ы).",
        'en': "%(count)d article(s) rejected.",
    },
    '%(count)d article(s) reset to draft.': {
        'uz': "%(count)d ta maqola qoralamaga qaytarildi.",
        'ru': "%(count)d статья(и) возвращена(ы) в черновик.",
        'en': "%(count)d article(s) reset to draft.",
    },
    '%(count)d article(s) sent to review.': {
        'uz': "%(count)d ta maqola ko'rib chiqishga yuborildi.",
        'ru': "%(count)d статья(и) отправлена(ы) на рецензирование.",
        'en': "%(count)d article(s) sent to review.",
    },
    '%(count)d reviewer(s) assigned.': {
        'uz': "%(count)d ta taqrizchi tayinlandi.",
        'ru': "%(count)d рецензент(ов) назначено.",
        'en': "%(count)d reviewer(s) assigned.",
    },
    'Access denied. Reviewers only.': {
        'uz': "Kirish taqiqlanadi. Faqat taqrizchilar uchun.",
        'ru': "Доступ запрещён. Только для рецензентов.",
        'en': "Access denied. Reviewers only.",
    },
    'Admin Decision At': {
        'uz': "Admin qaror vaqti",
        'ru': "Время решения администратора",
        'en': "Admin Decision At",
    },
    'Admin Decision By': {
        'uz': "Admin qaror beruvchi",
        'ru': "Решение принял",
        'en': "Admin Decision By",
    },
    'Admin Note': {
        'uz': "Admin izohi",
        'ru': "Заметка администратора",
        'en': "Admin Note",
    },
    'Admin can override policy and publish/reject directly': {
        'uz': "Admin siyosatni bekor qilib to'g'ridan-to'g'ri nashr/rad qilishi mumkin",
        'ru': "Администратор может обойти политику и опубликовать/отклонить напрямую",
        'en': "Admin can override policy and publish/reject directly",
    },
    'Administrator': {
        'uz': "Administrator",
        'ru': "Администратор",
        'en': "Administrator",
    },
    'Allow Admin Override': {
        'uz': "Admin bekor qilishga ruxsat",
        'ru': "Разрешить администратору переопределять",
        'en': "Allow Admin Override",
    },
    'Approve': {
        'uz': "Tasdiqlash",
        'ru': "Одобрить",
        'en': "Approve",
    },
    'Approved': {
        'uz': "Tasdiqlangan",
        'ru': "Одобрено",
        'en': "Approved",
    },
    'Article "%(title)s" has been published!': {
        'uz': '"%(title)s" maqolasi nashr qilindi!',
        'ru': 'Статья "%(title)s" опубликована!',
        'en': 'Article "%(title)s" has been published!',
    },
    'Article "%(title)s" has been resubmitted for review.': {
        'uz': '"%(title)s" maqolasi qayta ko\'rib chiqish uchun yuborildi.',
        'ru': 'Статья "%(title)s" отправлена на повторное рецензирование.',
        'en': 'Article "%(title)s" has been resubmitted for review.',
    },
    'Article "%(title)s" has been submitted for admin review.': {
        'uz': '"%(title)s" maqolasi admin ko\'rib chiqishi uchun yuborildi.',
        'ru': 'Статья "%(title)s" отправлена на рассмотрение администратора.',
        'en': 'Article "%(title)s" has been submitted for admin review.',
    },
    'Article For Review': {
        'uz': "Ko'rib chiqish uchun maqola",
        'ru': "Статья для рецензирования",
        'en': "Article For Review",
    },
    'Article Published': {
        'uz': "Maqola nashr qilindi",
        'ru': "Статья опубликована",
        'en': "Article Published",
    },
    'Article Resubmitted': {
        'uz': "Maqola qayta yuborildi",
        'ru': "Статья отправлена повторно",
        'en': "Article Resubmitted",
    },
    'Article Submitted': {
        'uz': "Maqola yuborildi",
        'ru': "Статья отправлена",
        'en': "Article Submitted",
    },
    'Article cannot be published in its current status.': {
        'uz': "Maqolani joriy holatda nashr qilib bo'lmaydi.",
        'ru': "Статью нельзя опубликовать в текущем статусе.",
        'en': "Article cannot be published in its current status.",
    },
    'Article cannot be rejected in its current status.': {
        'uz': "Maqolani joriy holatda rad etib bo'lmaydi.",
        'ru': "Статью нельзя отклонить в текущем статусе.",
        'en': "Article cannot be rejected in its current status.",
    },
    'Article cannot be submitted in its current status.': {
        'uz': "Maqolani joriy holatda yuborib bo'lmaydi.",
        'ru': "Статью нельзя отправить в текущем статусе.",
        'en': "Article cannot be submitted in its current status.",
    },
    'Article has been published successfully.': {
        'uz': "Maqola muvaffaqiyatli nashr qilindi.",
        'ru': "Статья успешно опубликована.",
        'en': "Article has been published successfully.",
    },
    'Article is blocked if rejections exceed this': {
        'uz': "Rad etishlar shu sondan oshsa maqola bloklanadi",
        'ru': "Статья блокируется, если количество отклонений превышает это значение",
        'en': "Article is blocked if rejections exceed this",
    },
    'Article is ready for publishing': {
        'uz': "Maqola nashr qilishga tayyor",
        'ru': "Статья готова к публикации",
        'en': "Article is ready for publishing",
    },
    'Article published successfully.': {
        'uz': "Maqola muvaffaqiyatli nashr qilindi.",
        'ru': "Статья успешно опубликована.",
        'en': "Article published successfully.",
    },
    'Article rejected.': {
        'uz': "Maqola rad etildi.",
        'ru': "Статья отклонена.",
        'en': "Article rejected.",
    },
    'Article resubmitted after changes': {
        'uz': "O'zgartirishlardan keyin maqola qayta yuborildi",
        'ru': "Статья отправлена повторно после изменений",
        'en': "Article resubmitted after changes",
    },
    'Article sent to review successfully.': {
        'uz': "Maqola ko'rib chiqishga muvaffaqiyatli yuborildi.",
        'ru': "Статья успешно отправлена на рецензирование.",
        'en': "Article sent to review successfully.",
    },
    'Article submitted successfully.': {
        'uz': "Maqola muvaffaqiyatli yuborildi.",
        'ru': "Статья успешно отправлена.",
        'en': "Article submitted successfully.",
    },
    'Assigned Reviewers': {
        'uz': "Tayinlangan taqrizchilar",
        'ru': "Назначенные рецензенты",
        'en': "Assigned Reviewers",
    },
    'Auto-publish only works when resubmitting after changes requested.': {
        'uz': "Avtomatik nashr faqat o'zgartirishlar so'ralgandan keyin qayta yuborilganda ishlaydi.",
        'ru': "Автоматическая публикация работает только при повторной отправке после запроса изменений.",
        'en': "Auto-publish only works when resubmitting after changes requested.",
    },
    'Biography': {
        'uz': "Biografiya",
        'ru': "Биография",
        'en': "Biography",
    },
    'Blocked': {
        'uz': "Bloklangan",
        'ru': "Заблокировано",
        'en': "Blocked",
    },
    'Blocked: Too many rejections (%(rejections)d > %(max)d)': {
        'uz': "Bloklangan: Juda ko'p rad etishlar (%(rejections)d > %(max)d)",
        'ru': "Заблокировано: Слишком много отклонений (%(rejections)d > %(max)d)",
        'en': "Blocked: Too many rejections (%(rejections)d > %(max)d)",
    },
    'Cannot request changes for article in its current status.': {
        'uz': "Joriy holatda maqolaga o'zgartirishlar so'rab bo'lmaydi.",
        'ru': "Нельзя запросить изменения для статьи в текущем статусе.",
        'en': "Cannot request changes for article in its current status.",
    },
    'Categories': {
        'uz': "Kategoriyalar",
        'ru': "Категории",
        'en': "Categories",
    },
    'Category': {
        'uz': "Kategoriya",
        'ru': "Категория",
        'en': "Category",
    },
    'Category Policies': {
        'uz': "Kategoriya siyosatlari",
        'ru': "Политики категорий",
        'en': "Category Policies",
    },
    'Category Policy': {
        'uz': "Kategoriya siyosati",
        'ru': "Политика категории",
        'en': "Category Policy",
    },
    'Changes Requested': {
        'uz': "O'zgartirishlar so'raldi",
        'ru': "Запрошены изменения",
        'en': "Changes Requested",
    },
    'Changes requested by %(count)d reviewer(s)': {
        'uz': "%(count)d ta taqrizchi tomonidan o'zgartirishlar so'raldi",
        'ru': "Изменения запрошены %(count)d рецензентом(ами)",
        'en': "Changes requested by %(count)d reviewer(s)",
    },
    'Changes requested for %(count)d article(s).': {
        'uz': "%(count)d ta maqolaga o'zgartirishlar so'raldi.",
        'ru': "Запрошены изменения для %(count)d статей.",
        'en': "Changes requested for %(count)d article(s).",
    },
    'Changes requested for your article': {
        'uz': "Maqolangizga o'zgartirishlar so'raldi",
        'ru': "Запрошены изменения для вашей статьи",
        'en': "Changes requested for your article",
    },
    'Changes requested from author.': {
        'uz': "Muallifdan o'zgartirishlar so'raldi.",
        'ru': "Запрошены изменения от автора.",
        'en': "Changes requested from author.",
    },
    'Comment': {
        'uz': "Izoh",
        'ru': "Комментарий",
        'en': "Comment",
    },
    'Comment is required when rejecting.': {
        'uz': "Rad etishda izoh talab qilinadi.",
        'ru': "При отклонении комментарий обязателен.",
        'en': "Comment is required when rejecting.",
    },
    'Comment is required when requesting changes.': {
        'uz': "O'zgartirishlar so'rashda izoh talab qilinadi.",
        'ru': "При запросе изменений комментарий обязателен.",
        'en': "Comment is required when requesting changes.",
    },
    'Content (English)': {
        'uz': "Mazmun (inglizcha)",
        'ru': "Содержание (английский)",
        'en': "Content (English)",
    },
    'Content (Russian)': {
        'uz': "Mazmun (ruscha)",
        'ru': "Содержание (русский)",
        'en': "Content (Russian)",
    },
    'Content (Uzbek)': {
        'uz': "Mazmun (o'zbekcha)",
        'ru': "Содержание (узбекский)",
        'en': "Content (Uzbek)",
    },
    'Decision': {
        'uz': "Qaror",
        'ru': "Решение",
        'en': "Decision",
    },
    'Description': {
        'uz': "Tavsif",
        'ru': "Описание",
        'en': "Description",
    },
    'General': {
        'uz': "Umumiy",
        'ru': "Общее",
        'en': "General",
    },
    'In Review': {
        'uz': "Ko'rib chiqilmoqda",
        'ru': "На рассмотрении",
        'en': "In Review",
    },
    'Keyword': {
        'uz': "Kalit so'z",
        'ru': "Ключевое слово",
        'en': "Keyword",
    },
    'Keywords': {
        'uz': "Kalit so'zlar",
        'ru': "Ключевые слова",
        'en': "Keywords",
    },
    'Maqola tasdiqlandi va nashr qilindi.': {
        'uz': "Maqola tasdiqlandi va nashr qilindi.",
        'ru': "Статья одобрена и опубликована.",
        'en': "Article approved and published.",
    },
    'Maqola tasdiqlandi.': {
        'uz': "Maqola tasdiqlandi.",
        'ru': "Статья одобрена.",
        'en': "Article approved.",
    },
    'Maximum Rejections Before Block': {
        'uz': "Bloklashdan oldingi maksimal rad etishlar",
        'ru': "Максимум отклонений перед блокировкой",
        'en': "Maximum Rejections Before Block",
    },
    'Minimum Approvals to Publish': {
        'uz': "Nashr uchun minimal tasdiqlashlar",
        'ru': "Минимум одобрений для публикации",
        'en': "Minimum Approvals to Publish",
    },
    'Minimum Required Reviews': {
        'uz': "Minimal talab qilinadigan taqrizlar",
        'ru': "Минимум необходимых рецензий",
        'en': "Minimum Required Reviews",
    },
    'N/A - Article is not in review': {
        'uz': "Yo'q — Maqola ko'rib chiqilmayapti",
        'ru': "Н/Д — Статья не на рецензировании",
        'en': "N/A - Article is not in review",
    },
    'Name (English)': {
        'uz': "Nomi (inglizcha)",
        'ru': "Название (английский)",
        'en': "Name (English)",
    },
    'Name (Russian)': {
        'uz': "Nomi (ruscha)",
        'ru': "Название (русский)",
        'en': "Name (Russian)",
    },
    'Name (Uzbek)': {
        'uz': "Nomi (o'zbekcha)",
        'ru': "Название (узбекский)",
        'en': "Name (Uzbek)",
    },
    'Needs more approvals: %(current)d/%(required)d': {
        'uz': "Ko'proq tasdiqlash kerak: %(current)d/%(required)d",
        'ru': "Нужно больше одобрений: %(current)d/%(required)d",
        'en': "Needs more approvals: %(current)d/%(required)d",
    },
    'Needs more reviews: %(current)d/%(required)d': {
        'uz': "Ko'proq taqriz kerak: %(current)d/%(required)d",
        'ru': "Нужно больше рецензий: %(current)d/%(required)d",
        'en': "Needs more reviews: %(current)d/%(required)d",
    },
    'New article assigned for review': {
        'uz': "Yangi maqola ko'rib chiqish uchun tayinlandi",
        'ru': "Новая статья назначена для рецензирования",
        'en': "New article assigned for review",
    },
    'New article submitted for review': {
        'uz': "Yangi maqola ko'rib chiqish uchun yuborildi",
        'ru': "Новая статья отправлена на рецензирование",
        'en': "New article submitted for review",
    },
    'No eligible articles selected.': {
        'uz': "Mos maqola tanlanmagan.",
        'ru': "Подходящие статьи не выбраны.",
        'en': "No eligible articles selected.",
    },
    'No notifications': {
        'uz': "Bildirishnomalar yo'q",
        'ru': "Нет уведомлений",
        'en': "No notifications",
    },
    'No pending articles selected.': {
        'uz': "Kutayotgan maqola tanlanmagan.",
        'ru': "Ожидающие статьи не выбраны.",
        'en': "No pending articles selected.",
    },
    'Notifications': {
        'uz': "Bildirishnomalar",
        'ru': "Уведомления",
        'en': "Notifications",
    },
    'Number of approval votes required': {
        'uz': "Talab qilinadigan tasdiqlash ovozlari soni",
        'ru': "Необходимое количество голосов за одобрение",
        'en': "Number of approval votes required",
    },
    'Only pending articles can be sent to review.': {
        'uz': "Faqat kutayotgan maqolalar ko'rib chiqishga yuborilishi mumkin.",
        'ru': "Только ожидающие статьи могут быть отправлены на рецензирование.",
        'en': "Only pending articles can be sent to review.",
    },
    'Only the author can submit this article.': {
        'uz': "Faqat muallif bu maqolani yuborishi mumkin.",
        'ru': "Только автор может отправить эту статью.",
        'en': "Only the author can submit this article.",
    },
    'Optional deadline for reviews': {
        'uz': "Taqrizlar uchun ixtiyoriy muddat",
        'ru': "Необязательный срок для рецензий",
        'en': "Optional deadline for reviews",
    },
    'Organization': {
        'uz': "Tashkilot",
        'ru': "Организация",
        'en': "Organization",
    },
    'Pending Admin Review': {
        'uz': "Admin ko'rib chiqishini kutmoqda",
        'ru': "Ожидает рассмотрения администратора",
        'en': "Pending Admin Review",
    },
    'Publishability': {
        'uz': "Nashr qilish imkoniyati",
        'ru': "Возможность публикации",
        'en': "Publishability",
    },
    'Published At': {
        'uz': "Nashr qilingan vaqt",
        'ru': "Дата публикации",
        'en': "Published At",
    },
    'Publish Articles': {
        'uz': "Maqolalarni nashr qilish",
        'ru': "Опубликовать статьи",
        'en': "Publish Articles",
    },
    'Read': {
        'uz': "O'qilgan",
        'ru': "Прочитано",
        'en': "Read",
    },
    'Ready for publishing': {
        'uz': "Nashr qilishga tayyor",
        'ru': "Готово к публикации",
        'en': "Ready for publishing",
    },
    'Ready to Publish': {
        'uz': "Nashr qilishga tayyor",
        'ru': "Готово к публикации",
        'en': "Ready to Publish",
    },
    'Reject': {
        'uz': "Rad etish",
        'ru': "Отклонить",
        'en': "Reject",
    },
    'Reject Articles': {
        'uz': "Maqolalarni rad etish",
        'ru': "Отклонить статьи",
        'en': "Reject Articles",
    },
    'Request Changes': {
        'uz': "O'zgartirishlarni so'rash",
        'ru': "Запросить изменения",
        'en': "Request Changes",
    },
    'Request Changes from Author': {
        'uz': "Muallifdan o'zgartirishlarni so'rash",
        'ru': "Запросить изменения у автора",
        'en': "Request Changes from Author",
    },
    'Require Comment for Changes': {
        'uz': "O'zgartirishlar uchun izoh talab qilinsin",
        'ru': "Требовать комментарий при запросе изменений",
        'en': "Require Comment for Changes",
    },
    'Require Comment for Rejection': {
        'uz': "Rad etish uchun izoh talab qilinsin",
        'ru': "Требовать комментарий при отклонении",
        'en': "Require Comment for Rejection",
    },
    'Reset to Draft': {
        'uz': "Qoralamaga qaytarish",
        'ru': "Вернуть в черновик",
        'en': "Reset to Draft",
    },
    'Review': {
        'uz': "Taqriz",
        'ru': "Рецензия",
        'en': "Review",
    },
    'Review Comment': {
        'uz': "Taqriz izohi",
        'ru': "Комментарий рецензии",
        'en': "Review Comment",
    },
    'Review Deadline (Hours)': {
        'uz': "Ko'rib chiqish muddati (soat)",
        'ru': "Срок рецензирования (часов)",
        'en': "Review Deadline (Hours)",
    },
    'Review In Progress': {
        'uz': "Ko'rib chiqish jarayonida",
        'ru': "Рецензирование в процессе",
        'en': "Review In Progress",
    },
    'Review Status by Category': {
        'uz': "Kategoriya bo'yicha taqriz holati",
        'ru': "Статус рецензирования по категориям",
        'en': "Review Status by Category",
    },
    'Review Submitted': {
        'uz': "Taqriz yuborildi",
        'ru': "Рецензия отправлена",
        'en': "Review Submitted",
    },
    'Review in progress': {
        'uz': "Ko'rib chiqish jarayonida",
        'ru': "Рецензирование в процессе",
        'en': "Review in progress",
    },
    'Review received for your article': {
        'uz': "Maqolangiz uchun taqriz keldi",
        'ru': "Получена рецензия для вашей статьи",
        'en': "Review received for your article",
    },
    'Reviewer': {
        'uz': "Taqrizchi",
        'ru': "Рецензент",
        'en': "Reviewer",
    },
    'Reviewer Assigned': {
        'uz': "Taqrizchi tayinlandi",
        'ru': "Рецензент назначен",
        'en': "Reviewer Assigned",
    },
    'Reviewer Assignment': {
        'uz': "Taqrizchi tayinlovi",
        'ru': "Назначение рецензента",
        'en': "Reviewer Assignment",
    },
    'Reviewer Dashboard': {
        'uz': "Taqrizchi paneli",
        'ru': "Панель рецензента",
        'en': "Reviewer Dashboard",
    },
    'Reviewer feedback or comment': {
        'uz': "Taqrizchining fikr-mulohazasi yoki izohi",
        'ru': "Отзыв или комментарий рецензента",
        'en': "Reviewer feedback or comment",
    },
    'Reviewer must provide comment when rejecting': {
        'uz': "Taqrizchi rad etishda izoh berishi kerak",
        'ru': "Рецензент должен предоставить комментарий при отклонении",
        'en': "Reviewer must provide comment when rejecting",
    },
    'Reviewer must provide comment when requesting changes': {
        'uz': "Taqrizchi o'zgartirishlar so'rashda izoh berishi kerak",
        'ru': "Рецензент должен предоставить комментарий при запросе изменений",
        'en': "Reviewer must provide comment when requesting changes",
    },
    'Reviewers can only be assigned to pending or in-review articles.': {
        'uz': "Taqrizchilar faqat kutayotgan yoki ko'rib chiqilayotgan maqolalarga tayinlanishi mumkin.",
        'ru': "Рецензентов можно назначить только на ожидающие или находящиеся на рецензировании статьи.",
        'en': "Reviewers can only be assigned to pending or in-review articles.",
    },
    'Reviewers who can review articles in this category': {
        'uz': "Bu kategoriyada maqolalarni ko'rib chiqishi mumkin bo'lgan taqrizchilar",
        'ru': "Рецензенты, которые могут рецензировать статьи в этой категории",
        'en': "Reviewers who can review articles in this category",
    },
    'Reviews': {
        'uz': "Taqrizlar",
        'ru': "Рецензии",
        'en': "Reviews",
    },
    'Send to Review (from Pending Admin)': {
        'uz': "Ko'rib chiqishga yuborish (Admin kutmoqda holatidan)",
        'ru': "Отправить на рецензирование (из статуса «Ожидает администратора»)",
        'en': "Send to Review (from Pending Admin)",
    },
    'Status Changed': {
        'uz': "Holat o'zgartirildi",
        'ru': "Статус изменён",
        'en': "Status Changed",
    },
    'This article cannot be reviewed in its current status.': {
        'uz': "Bu maqolani joriy holatda ko'rib chiqib bo'lmaydi.",
        'ru': "Эту статью нельзя рецензировать в текущем статусе.",
        'en': "This article cannot be reviewed in its current status.",
    },
    'Title (English)': {
        'uz': "Sarlavha (inglizcha)",
        'ru': "Заголовок (английский)",
        'en': "Title (English)",
    },
    'Title (Russian)': {
        'uz': "Sarlavha (ruscha)",
        'ru': "Заголовок (русский)",
        'en': "Title (Russian)",
    },
    'Title (Uzbek)': {
        'uz': "Sarlavha (o'zbekcha)",
        'ru': "Заголовок (узбекский)",
        'en': "Title (Uzbek)",
    },
    'Total reviews needed before decision': {
        'uz': "Qaror qabul qilishdan oldin kerakli jami taqrizlar",
        'ru': "Общее количество рецензий перед принятием решения",
        'en': "Total reviews needed before decision",
    },
    'Upload article file (PDF, DOC, DOCX). Max 20MB.': {
        'uz': "Maqola faylini yuklang (PDF, DOC, DOCX). Maksimum 20MB.",
        'ru': "Загрузите файл статьи (PDF, DOC, DOCX). Максимум 20 МБ.",
        'en': "Upload article file (PDF, DOC, DOCX). Max 20MB.",
    },
    'You are not assigned to review this category.': {
        'uz': "Sizga bu kategoriyani ko'rib chiqish tayinlanmagan.",
        'ru': "Вам не назначено рецензирование этой категории.",
        'en': "You are not assigned to review this category.",
    },
    'You have been assigned as a Reviewer': {
        'uz': "Siz taqrizchi sifatida tayinlandingiz",
        'ru': "Вы назначены рецензентом",
        'en': "You have been assigned as a Reviewer",
    },
    'You have been assigned to review an article': {
        'uz': "Sizga maqolani ko'rib chiqish tayinlandi",
        'ru': "Вам назначено рецензирование статьи",
        'en': "You have been assigned to review an article",
    },
    'Your article has been published!': {
        'uz': "Maqolangiz nashr qilindi!",
        'ru': "Ваша статья опубликована!",
        'en': "Your article has been published!",
    },
    'Your article has been rejected': {
        'uz': "Maqolangiz rad etildi",
        'ru': "Ваша статья отклонена",
        'en': "Your article has been rejected",
    },
    'Your review has been submitted.': {
        'uz': "Taqrizingiz yuborildi.",
        'ru': "Ваша рецензия отправлена.",
        'en': "Your review has been submitted.",
    },
    '[%(site_name)s] Review submitted: %(title)s': {
        'uz': "[%(site_name)s] Taqriz yuborildi: %(title)s",
        'ru': "[%(site_name)s] Рецензия отправлена: %(title)s",
        'en': "[%(site_name)s] Review submitted: %(title)s",
    },
}


def add_translations():
    languages = ['uz', 'ru', 'en']
    
    for lang in languages:
        po_path = f'locale/{lang}/LC_MESSAGES/django.po'
        if not os.path.exists(po_path):
            print(f"WARNING: {po_path} does not exist, skipping")
            continue
        
        po = polib.pofile(po_path)
        existing = {e.msgid for e in po}
        
        added = 0
        for msgid, translations in TRANSLATIONS.items():
            if msgid not in existing:
                msgstr = translations.get(lang, '')
                entry = polib.POEntry(
                    msgid=msgid,
                    msgstr=msgstr,
                )
                po.append(entry)
                added += 1
        
        if added > 0:
            po.save()
            print(f"{lang.upper()}: Added {added} new translations")
        else:
            print(f"{lang.upper()}: No new translations needed")
    
    # Compile
    for lang in languages:
        po_path = f'locale/{lang}/LC_MESSAGES/django.po'
        mo_path = f'locale/{lang}/LC_MESSAGES/django.mo'
        if os.path.exists(po_path):
            po = polib.pofile(po_path)
            po.save_as_mofile(mo_path)
            print(f"{lang.upper()}: Compiled .mo file ({len(po)} entries)")


if __name__ == '__main__':
    add_translations()
