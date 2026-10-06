const form = document.getElementById('signupForm');
const formStatus = document.getElementById('formStatus');
const customersTableBody = document.getElementById('customersTableBody');
const customerCount = document.getElementById('customerCount');
const adminTableBody = document.getElementById('adminTableBody');
const adminCount = document.getElementById('adminCount');
const exportBtn = document.getElementById('exportBtn');
const clearBtn = document.getElementById('clearBtn');
const adminLoginCard = document.getElementById('adminLoginCard');
const adminDashboard = document.getElementById('adminDashboard');
const loginBtn = document.getElementById('loginBtn');
const loginMessage = document.getElementById('loginMessage');
const adminPasswordInput = document.getElementById('adminPassword');
const totalStudentsEl = document.getElementById('totalStudents');
const topCourseEl = document.getElementById('topCourse');
const monthlyCountEl = document.getElementById('monthlyCount');
const ADMIN_PASSWORD = 'admin123';

function updateAdminVisibility() {
  const isAuthenticated = localStorage.getItem('academyAdmin') === 'true';
  if (adminLoginCard && adminDashboard) {
    adminLoginCard.style.display = isAuthenticated ? 'none' : 'block';
    adminDashboard.classList.toggle('admin-hidden', !isAuthenticated);
  }
}

function updateStats(customers) {
  if (!Array.isArray(customers)) return;

  const total = customers.length;
  const counts = {};
  let monthly = 0;

  const now = new Date();
  customers.forEach((customer) => {
    const course = customer.course || 'Boshqa';
    counts[course] = (counts[course] || 0) + 1;

    const registered = customer.registered_at ? new Date(customer.registered_at) : null;
    if (registered && registered.getMonth() === now.getMonth() && registered.getFullYear() === now.getFullYear()) {
      monthly += 1;
    }
  });

  const bestCourse = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];

  if (totalStudentsEl) totalStudentsEl.textContent = String(total);
  if (topCourseEl) topCourseEl.textContent = bestCourse ? bestCourse[0] : '-';
  if (monthlyCountEl) monthlyCountEl.textContent = String(monthly);
}

async function loadCustomers() {
  try {
    const response = await fetch('/api/customers');
    const customers = await response.json();

    const targetBody = customersTableBody || adminTableBody;
    const targetCount = customerCount || adminCount;

    if (!targetBody) return;

    if (!Array.isArray(customers) || customers.length === 0) {
      targetBody.innerHTML = `
        <tr>
          <td colspan="5">Hozircha ro'yxatdan o'tgan mijozlar yo'q.</td>
        </tr>
      `;
      if (targetCount) targetCount.textContent = '0 ta';
      updateStats([]);
      return;
    }

    const rows = customers
      .slice()
      .reverse()
      .map(
        (customer) => `
          <tr>
            <td>${customer.name || '-'}</td>
            <td>${customer.phone || '-'}</td>
            <td>${customer.email || '-'}</td>
            <td>${customer.course || '-'}</td>
            <td>${customer.registered_at || '-'}</td>
          </tr>
        `
      )
      .join('');

    targetBody.innerHTML = rows;
    if (targetCount) targetCount.textContent = `${customers.length} ta`;
    updateStats(customers);
  } catch (error) {
    const targetBody = customersTableBody || adminTableBody;
    const targetCount = customerCount || adminCount;
    if (targetBody) {
      targetBody.innerHTML = `
        <tr>
          <td colspan="5">Mijozlar ro'yxati yuklanmadi.</td>
        </tr>
      `;
    }
    if (targetCount) targetCount.textContent = '0 ta';
    updateStats([]);
  }
}

if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = document.getElementById('name').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const email = document.getElementById('email').value.trim();
    const course = document.getElementById('course').value;

    if (!name || !phone || !email) {
      formStatus.textContent = 'Iltimos, barcha maydonlarni toʻldiring.';
      formStatus.style.color = '#b42318';
      return;
    }

    formStatus.textContent = 'Ma’lumotlar yuborilmoqda...';
    formStatus.style.color = '#1f4ed8';

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, phone, email, course }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || 'Xatolik yuz berdi.');
      }

      formStatus.textContent = `${name}, ${course} kursi uchun arizangiz qabul qilindi. Ma’lumotlar sizga jo‘natiladi.`;
      formStatus.style.color = '#1bbf74';
      form.reset();
      loadCustomers();
    } catch (error) {
      formStatus.textContent = error.message || 'Xatolik yuz berdi.';
      formStatus.style.color = '#b42318';
    }
  });
}

if (loginBtn) {
  loginBtn.addEventListener('click', () => {
    const entered = adminPasswordInput ? adminPasswordInput.value.trim() : '';
    if (entered === ADMIN_PASSWORD) {
      localStorage.setItem('academyAdmin', 'true');
      updateAdminVisibility();
      loadCustomers();
      if (loginMessage) {
        loginMessage.textContent = 'Kirish muvaffaqiyatli bajarildi.';
        loginMessage.style.color = '#1bbf74';
      }
      return;
    }

    if (loginMessage) {
      loginMessage.textContent = 'Noto\'g\'ri parol. Demo parol: admin123';
      loginMessage.style.color = '#b42318';
    }
  });
}

if (exportBtn) {
  exportBtn.addEventListener('click', async () => {
    window.location.href = '/api/customers/export';
  });
}

if (clearBtn) {
  clearBtn.addEventListener('click', async () => {
    const confirmed = window.confirm('Haqiqatan ham barcha mijozlar ro\'yxatini tozalaysizmi?');
    if (!confirmed) return;

    const response = await fetch('/api/customers/clear', { method: 'POST' });
    const result = await response.json();
    alert(result.message || 'Ro\'yxat tozalandi.');
    loadCustomers();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  updateAdminVisibility();
  loadCustomers();
});
