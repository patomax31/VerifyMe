/* ═══════════════════════════════════════════════════════════════════════
   VerifyMe · app.js  — sin conflictos de merge
═══════════════════════════════════════════════════════════════════════ */

// ════ GLOBALES DE CAMARA Y TIMERS ════
let regStream = null;
let regAdminStream = null;
let loginStream = null;
let loginInterval = null;

const loginVideo = document.getElementById('loginVideo');
const regVideo = document.getElementById('regVideo');
const regAdminVideo = document.getElementById('regAdminVideo');

const loginImage = document.getElementById('loginImage');
const regImage = document.getElementById('regImage');
let regAdminImage = regAdminVideo ? document.createElement('img') : null; // For mjpeg fallback

if (regAdminImage && regAdminVideo && regAdminVideo.parentNode) {
  regAdminImage.id = 'regAdminImage';
  regAdminImage.style.display = 'none';
  regAdminVideo.parentNode.insertBefore(regAdminImage, regAdminVideo);
}

// ════ ACCESO FACIAL DOM ════
const camOverlay = document.getElementById('cameraOverlay');
const loginStart = document.getElementById('loginStart');
const loginStop = document.getElementById('loginStop');
const loginMsg = document.getElementById('loginMessage');
const loginMsgHelp = document.getElementById('loginMessageHelp');
const loginHelpModal = document.getElementById('loginHelpModal');
const loginHelpOverlay = document.getElementById('loginHelpOverlay');
const loginHelpClose = document.getElementById('loginHelpClose');

// ════ REGISTRO BIOMÉTRICO DOM ════
let regStepIndex = 0;
const regStart = document.getElementById('regStart');
const regCapture = document.getElementById('regCapture');
const regStop = document.getElementById('regStop');
const regMsg = document.getElementById('regMessage');
const regCamOv = document.getElementById('regCameraOverlay');

// ════ REGISTRO ADMIN DOM ════
let regAdminStepIndex = 0;
const regAdminStart = document.getElementById('regAdminStart');
const regAdminCapture = document.getElementById('regAdminCapture');
const regAdminStop = document.getElementById('regAdminStop');
const regAdminMsg = document.getElementById('regAdminMessage');
const regAdminCamOv = document.getElementById('regAdminCameraOverlay');

// ════ I18N ════
const I18N = {
  es: {
    nav_home:'Inicio', nav_access:'Acceso facial', nav_register:'Registro facial', nav_admin:'Admin panel',
    logout:'Cerrar sesión',
    home_eyebrow:'Bienvenido', home_title:'Panel principal',
    home_sub:'Dashboard escolar para acceso facial, registro biométrico y administración.',
    stat_students:'Estudiantes', stat_active:'Activos',
    status_online:'Sistema en línea', status_sub:'Cámara activa · Modelo listo', status_badge:'Operando',
    last_access:'Últimos accesos', no_records:'Sin registros recientes', qnav_register:'Registrar alumno',
    title_home:'Panel principal', title_access:'Acceso facial', title_register:'Registro biométrico', title_admin:'Admin panel',
    step1of2:'Paso 1 de 2', step2of2:'Paso 2 de 2',
    access_sub:'Posiciona el rostro del alumno frente a la cámara.',
    liveness_init:'Inicia la cámara para comenzar la verificación.',
    cam_stopped:'Cámara detenida', btn_start_cam:'Iniciar cámara', btn_stop:'Detener',
    scanning:'Escaneando...',
    waiting_face:'ESPERANDO ROSTRO...', result_title:'Resultado', btn_scan_another:'Escanear otro alumno',
    reg_title_data:'Datos del alumno', reg_sub_data:'Ingresa la información escolar.',
    field_name:'Nombre completo', field_grade:'Grado', field_group:'Grupo', field_shift:'Turno',
    btn_go_camera:'Continuar a cámara',
    reg_title_cam:'Captura biométrica', reg_sub_cam:'Captura 3 ángulos: frente, izquierdo y derecho.',
    angle_front:'Frente', angle_left:'Izquierda', angle_right:'Derecha',
    angle_hint_front:'Mira de frente a la cámara. Esta foto será tu credencial.',
    angle_hint_left:'Gira la cabeza hacia tu izquierda.',
    angle_hint_right:'Gira la cabeza hacia tu derecha. Luego pulsa el botón.',
    btn_capture_front:'Capturar frente', btn_capture_left:'Capturar perfil izq.', btn_save_student:'Registrar alumno',
    reg_start_cam:'Inicia la cámara y sigue los pasos.', btn_edit_data:'Editar datos',
    reg_cam_ready:'Cámara lista. Sigue los pasos.', reg_saved_angle:'Captura guardada. Siguiente ángulo.',
    reg_success:'¡Alumno registrado exitosamente!', reg_error:'Error al registrar.', reg_conn_error:'Error de conexión.',
    admin_sub:'Gestión escolar, parámetros del modelo y administradores.',
    tab_students:'Estudiantes', tab_model:'Modelo', tab_admins:'Admins', tab_logs:'Logs',
    tab_dashboard:'Dashboard', tab_hardware:'Hardware',
    btn_create_student:'Crear', btn_refresh:'Refrescar',
    students_mgmt:'Gestión de estudiantes.',
    no_camera:'No se pudo acceder a la cámara.',
    clock_status:'SISTEMA EN LÍNEA · CÁMARA ACTIVA',
    dash_students:'Estudiantes', dash_admins:'Admins', dash_access_logs:'Registros de acceso',
    dash_refresh:'Refrescar', dash_create:'Crear', dash_students_hint:'Estudiantes registrados.',
    dash_admins_hint:'Administradores activos.', dash_logs_hint:'Registros de la sesion activa.',
    dash_log_time:'Hora', dash_log_user:'Usuario', dash_log_event:'Evento', dash_log_result:'Resultado',
    dash_no_session:'No hay sesion activa.', dash_no_logs:'Sin registros.',
    dash_status:'Estado', dash_active:'Activo', dash_inactive:'Inactivo',
    dash_employee:'No. empleado', dash_name:'Nombre', dash_role:'Rol', dash_email:'Correo',
    dash_password:'Password', dash_save:'Guardar', dash_cancel:'Cancelar',
    dash_photo_title:'Foto de estudiante',
    servo_response:'Tiempo de respuesta (s)', servo_always_active:'Siempre activo',
    servo_on:'Si', servo_off:'No', servo_load:'Cargar', servo_save:'Guardar',
    servo_hint:'Configura el tiempo de apertura del torniquete.',
    logs_sub:'Registros de acceso con filtros.',
    log_filter_all:'Todos',
    log_filter_event:'Evento',
    log_filter_result:'Resultado',
    log_filter_name:'Nombre',
    log_filter_search:'Buscar',
    log_filter_clear:'Limpiar',
    log_event_entry:'Entrada',
    log_event_exit:'Salida',
    log_result_ok:'OK',
    log_result_denied:'Denegado',
    log_msg_ready:'Mostrando ultimos registros.',
    log_no_records:'Sin registros.',
    log_col_time:'Fecha',
    log_col_name:'Nombre',
    log_col_grade:'Grado',
    log_col_group:'Grupo',
    log_col_shift:'Turno',
    log_col_event:'Evento',
    log_col_result:'Resultado',
  },
  en: {
    nav_home:'Home', nav_access:'Facial access', nav_register:'Facial register', nav_admin:'Admin panel',
    logout:'Log out',
    home_eyebrow:'Welcome', home_title:'Main panel',
    home_sub:'School dashboard for facial access, biometric registration and administration.',
    stat_students:'Students', stat_active:'Active',
    status_online:'System online', status_sub:'Camera active · Model ready', status_badge:'Operating',
    last_access:'Recent access', no_records:'No recent records', qnav_register:'Register student',
    title_home:'Main panel', title_access:'Facial access', title_register:'Biometric register', title_admin:'Admin panel',
    step1of2:'Step 1 of 2', step2of2:'Step 2 of 2',
    access_sub:"Position the student's face in front of the camera.",
    liveness_init:'Start the camera to begin verification.',
    cam_stopped:'Camera stopped', btn_start_cam:'Start camera', btn_stop:'Stop',
    scanning:'Scanning...',
    waiting_face:'WAITING FOR FACE...', result_title:'Result', btn_scan_another:'Scan another student',
    reg_title_data:'Student data', reg_sub_data:'Enter school information.',
    field_name:'Full name', field_grade:'Grade', field_group:'Group', field_shift:'Shift',
    btn_go_camera:'Continue to camera',
    reg_title_cam:'Biometric capture', reg_sub_cam:'Capture 3 angles: front, left, right.',
    angle_front:'Front', angle_left:'Left', angle_right:'Right',
    angle_hint_front:'Look straight at the camera. This will be your ID photo.',
    angle_hint_left:'Turn your head to your left.',
    angle_hint_right:'Turn your head to your right. Then press the button.',
    btn_capture_front:'Capture front', btn_capture_left:'Capture left profile', btn_save_student:'Save student',
    reg_start_cam:'Start the camera and follow the steps.', btn_edit_data:'Edit data',
    reg_cam_ready:'Camera ready. Follow the steps.', reg_saved_angle:'Saved. Continue with next angle.',
    reg_success:'Student registered successfully!', reg_error:'Registration error.', reg_conn_error:'Connection error.',
    admin_sub:'School management, model settings and administrators.',
    tab_students:'Students', tab_model:'Model', tab_admins:'Admins', tab_logs:'Logs',
    tab_dashboard:'Dashboard', tab_hardware:'Hardware',
    btn_create_student:'Create', btn_refresh:'Refresh',
    students_mgmt:'Student management.',
    no_camera:'Could not access camera.',
    clock_status:'SYSTEM ONLINE · CAMERA ACTIVE',
    dash_students:'Students', dash_admins:'Admins', dash_access_logs:'Access logs',
    dash_refresh:'Refresh', dash_create:'Create', dash_students_hint:'Registered students.',
    dash_admins_hint:'Active admins.', dash_logs_hint:'Active session logs.',
    dash_log_time:'Time', dash_log_user:'User', dash_log_event:'Event', dash_log_result:'Result',
    dash_no_session:'No active session.', dash_no_logs:'No records.',
    dash_status:'Status', dash_active:'Active', dash_inactive:'Inactive',
    dash_employee:'Employee no.', dash_name:'Name', dash_role:'Role', dash_email:'Email',
    dash_password:'Password', dash_save:'Save', dash_cancel:'Cancel',
    dash_photo_title:'Student photo',
    servo_response:'Response time (s)', servo_always_active:'Always active',
    servo_on:'Yes', servo_off:'No', servo_load:'Load', servo_save:'Save',
    servo_hint:'Configure how long the turnstile stays open.',
    logs_sub:'Access records with filters.',
    log_filter_all:'All',
    log_filter_event:'Event',
    log_filter_result:'Result',
    log_filter_name:'Name',
    log_filter_search:'Search',
    log_filter_clear:'Clear',
    log_event_entry:'Entry',
    log_event_exit:'Exit',
    log_result_ok:'OK',
    log_result_denied:'Denied',
    log_msg_ready:'Showing latest records.',
    log_no_records:'No records.',
    log_col_time:'Date',
    log_col_name:'Name',
    log_col_grade:'Grade',
    log_col_group:'Group',
    log_col_shift:'Shift',
    log_col_event:'Event',
    log_col_result:'Result',
  },
};

let currentLang = localStorage.getItem('vm_lang') || 'es';
function t(k) { return I18N[currentLang][k] || I18N.es[k] || k; }

function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem('vm_lang', lang);
  document.documentElement.lang = lang;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const v = I18N[lang][el.dataset.i18n];
    if (v !== undefined) el.textContent = v;
  });
  const flagEl  = document.getElementById('langFlag');
  const labelEl = document.getElementById('langLabel');
  if (flagEl)  flagEl.textContent  = lang === 'es' ? 'MX' : 'US';
  if (labelEl) labelEl.textContent = lang === 'es' ? 'ES' : 'EN';
  updateRegAngleUi();
  const statusTxt = document.getElementById('covStatusTxt');
  if (statusTxt) statusTxt.textContent = t('clock_status');
}

document.getElementById('langBtn')?.addEventListener('click', () => {
  applyLang(currentLang === 'es' ? 'en' : 'es');
});

// ════ DRAWER ════
const drawer        = document.getElementById('drawer');
const drawerOverlay = document.getElementById('drawerOverlay');
const drawerAuthBtn = document.getElementById('drawerAuthBtn');

let drawerUnlocked = false;

function syncDrawerAuthUi() {
  if (!drawerAuthBtn) return;
  const icon = drawerAuthBtn.querySelector('.material-symbols-outlined');
  if (icon) icon.textContent = drawerUnlocked ? 'lock_open' : 'lock';
  const label = drawerUnlocked ? 'Abrir menú de administrador' : 'Desbloquear menú de administrador';
  drawerAuthBtn.setAttribute('aria-label', label);
  drawerAuthBtn.setAttribute('title', label);
}

function unlockDrawerAccess() {
  drawerUnlocked = true;
  document.body.classList.add('drawer-unlocked');
  syncDrawerAuthUi();
  openDrawer();
}

function requestDrawerUnlock() {
  const pass = prompt('Ingresa la contraseña de administrador:');
  if (pass === null) return;
  if (pass === ADMIN_DRAWER_PASSWORD) {
    unlockDrawerAccess();
    return;
  }
  alert('Contraseña incorrecta');
}

function openDrawer()  {
  if (!drawerUnlocked) return;
  drawer?.classList.add('open');
  drawerOverlay?.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeDrawer() {
  drawer?.classList.remove('open');
  drawerOverlay?.classList.remove('open');
  document.body.style.overflow = '';
}

document.getElementById('hamburger')?.addEventListener('click', openDrawer);
drawerAuthBtn?.addEventListener('click', () => {
  if (drawerUnlocked) {
    openDrawer();
    return;
  }
  requestDrawerUnlock();
});
document.getElementById('drawerClose')?.addEventListener('click', closeDrawer);
drawerOverlay?.addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeDrawer(); closeClockOverlay(); }
});

syncDrawerAuthUi();

// ════ NAVEGACIÓN ════
const allViews = document.querySelectorAll('.view');
const navBtns  = document.querySelectorAll('.nav-btn[data-view]');

function showView(viewId) {
  if (viewId !== 'access')   stopLoginCamera();
  if (viewId !== 'register') stopRegCamera();
  if (viewId !== 'register-admin') stopRegAdminCamera();

  // Animación de salida en la vista actual
  const current = document.querySelector('.view:not(.hidden)');
  if (current) current.classList.add('view-exit');

  setTimeout(() => {
    allViews.forEach(v => { v.classList.add('hidden'); v.classList.remove('view-exit', 'view-enter'); });
    navBtns.forEach(b => b.classList.remove('active'));

    const target = document.getElementById('view-' + viewId);
    if (target) {
      target.classList.remove('hidden');
      target.classList.add('view-enter');
      requestAnimationFrame(() => requestAnimationFrame(() => target.classList.remove('view-enter')));
    }

    const btn = document.querySelector('.nav-btn[data-view="' + viewId + '"]');
    if (btn) btn.classList.add('active');

    const titleEl = document.getElementById('topbarTitle');
    if (titleEl) titleEl.textContent = t('title_' + viewId) || viewId;

    closeDrawer();

    // Auto-iniciar cámara al entrar a acceso facial
    if (viewId === 'access') {
      showAccessStep(1);
      setTimeout(startLoginCameraAuto, 300);
    }
  }, 180);
}

navBtns.forEach(b => b.addEventListener('click', () => showView(b.dataset.view)));

document.querySelectorAll('[data-goto]').forEach(b => {
  b.addEventListener('click', () => showView(b.dataset.goto));
});

const urlView = new URLSearchParams(window.location.search).get('view');
if (urlView && ['access','register','admin'].includes(urlView)) {
  showView(urlView);
} else {
  showView('access'); // Redirigir a login / acceso facial por defecto
}

// ════ RELOJ TOPBAR ════
function updateClock() {
  const locale = currentLang === 'es' ? 'es-MX' : 'en-US';
  const now = new Date();
  const hh  = now.toLocaleTimeString(locale, { hour:'2-digit', minute:'2-digit', hour12:false });
  const dd  = now.toLocaleDateString(locale,  { weekday:'short', day:'numeric', month:'short' });
  const h = document.getElementById('clockH');
  const d = document.getElementById('clockD');
  if (h) h.textContent = hh;
  if (d) d.textContent = dd.replace(/\./g,'').replace(/,/g,'');
}
updateClock();
setInterval(updateClock, 1000);

// ════ CLOCK OVERLAY ════
const clockOverlay = document.getElementById('clockOverlay');
let clockInterval   = null;
let inactivityTimer = null;
let countdownTimer  = null;
let countdownInterval = null;

const INACTIVITY_MS  = 60000;
const COUNTDOWN_SECS = 10;

const clockToast    = document.getElementById('clockToast');
const toastNum      = document.getElementById('toastNum');
const toastProgress = document.getElementById('toastProgress');
const toastCancel   = document.getElementById('toastCancel');

const CIRC = 82;

const DAYS_ES   = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
const DAYS_EN   = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
const MONTHS_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
const MONTHS_EN = ['January','February','March','April','May','June','July','August','September','October','November','December'];

function tickClockOverlay() {
  const now  = new Date();
  const h    = now.getHours();
  const m    = now.getMinutes();
  const s    = now.getSeconds();
  const ampm = h >= 12 ? 'PM' : 'AM';
  const h12  = h % 12 || 12;

  const days   = currentLang === 'es' ? DAYS_ES   : DAYS_EN;
  const months = currentLang === 'es' ? MONTHS_ES : MONTHS_EN;
  const dateStr = currentLang === 'es'
    ? `${days[now.getDay()]}, ${now.getDate()} de ${months[now.getMonth()]} ${now.getFullYear()}`
    : `${days[now.getDay()]}, ${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`;

  const covH  = document.getElementById('covH');
  const covM  = document.getElementById('covM');
  const covAP = document.getElementById('covAMPM');
  const covD  = document.getElementById('covDate');
  const covS  = document.getElementById('covSeconds');

  if (covH)  covH.textContent  = String(h12).padStart(2,'0');
  if (covM)  covM.textContent  = String(m).padStart(2,'0');
  if (covAP) covAP.textContent = ampm;
  if (covD)  covD.textContent  = dateStr;
  if (covS)  covS.textContent  = String(s).padStart(2,'0') + 's';
}

function openClockOverlay() {
  if (!clockOverlay) return;
  stopCountdown();
  stopInactivityTimer();
  hideToast();
  clockOverlay.classList.remove('hidden');
  clockOverlay.getBoundingClientRect();
  clockOverlay.classList.add('visible');
  document.body.style.overflow = 'hidden';
  tickClockOverlay();
  clockInterval = setInterval(tickClockOverlay, 1000);
}

function closeClockOverlay() {
  if (!clockOverlay) return;
  clockOverlay.classList.remove('visible');
  document.body.style.overflow = '';
  clearInterval(clockInterval);
  clockInterval = null;
  setTimeout(() => {
    if (!clockOverlay.classList.contains('visible')) {
      clockOverlay.classList.add('hidden');
    }
  }, 650);
  resetInactivityTimer();
}

function showToast() {
  if (!clockToast) return;
  let secs = COUNTDOWN_SECS;
  if (toastNum) toastNum.textContent = secs;
  if (toastProgress) toastProgress.style.strokeDashoffset = 0;
  clockToast.classList.add('visible');

  countdownInterval = setInterval(() => {
    secs--;
    if (toastNum) toastNum.textContent = secs;
    const offset = CIRC * (1 - secs / COUNTDOWN_SECS);
    if (toastProgress) toastProgress.style.strokeDashoffset = offset;
    if (secs <= 0) {
      stopCountdown();
      hideToast();
      openClockOverlay();
    }
  }, 1000);
}

function hideToast() {
  if (!clockToast) return;
  clockToast.classList.remove('visible');
  clearInterval(countdownInterval);
  countdownInterval = null;
}

function stopCountdown() {
  hideToast();
  clearTimeout(countdownTimer);
  countdownTimer = null;
}

function resetInactivityTimer() {
  clearTimeout(inactivityTimer);
  stopCountdown();
  inactivityTimer = setTimeout(() => {
    showToast();
  }, INACTIVITY_MS);
}

function stopInactivityTimer() {
  clearTimeout(inactivityTimer);
  inactivityTimer = null;
  stopCountdown();
}

toastCancel?.addEventListener('click', e => {
  e.stopPropagation();
  stopCountdown();
  resetInactivityTimer();
});

['click','touchstart','mousemove','keydown','scroll','pointerdown'].forEach(ev => {
  document.addEventListener(ev, () => {
    if (!clockOverlay?.classList.contains('visible')) {
      if (clockToast?.classList.contains('visible')) {
        stopCountdown();
        resetInactivityTimer();
        return;
      }
      resetInactivityTimer();
    }
  }, { passive: true });
});

clockOverlay?.addEventListener('click', () => {
  closeClockOverlay();
  showView('access');
});

document.getElementById('clockModeBtn')?.addEventListener('click', e => {
  e.stopPropagation();
  openClockOverlay();
});

openClockOverlay();

// ════ HOME STATS ════
function animateCount(el, target, duration = 900) {
  if (!el) return;
  const start = performance.now();
  const from  = parseInt(el.textContent) || 0;
  const step  = ts => {
    const progress = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (target - from) * ease);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

async function fetchHomeStats() {
  try {
    const res  = await fetch('/api/admin/students');
    const data = await res.json();
    const list = data.students || data || [];
    const tot  = document.getElementById('statTotal');
    const act  = document.getElementById('statActivos');
    animateCount(tot, list.length);
    animateCount(act, list.filter(s => s.activo !== false).length);

    // Últimos accesos (mock si no hay endpoint)
    renderLastAccess(list.slice(-4).reverse());
  } catch (_) {}
}

function renderLastAccess(list) {
  const container = document.getElementById('lastAccessList');
  if (!container) return;
  if (!list.length) return;
  container.innerHTML = list.map(s => {
    const initials = (s.nombre||'??').split(' ').map(w => w[0]).join('').slice(0,2).toUpperCase();
    const colors   = ['#006B28','#008A34','#004D1C','#1E5530'];
    const color    = colors[(s.id || 0) % colors.length];
    return `
      <div class="access-item" style="--accent:${color}">
        <div class="access-item__avatar" style="background:${color}">${initials}</div>
        <div class="access-item__info">
          <span class="access-item__name">${s.nombre}</span>
          <span class="access-item__meta">${s.grado}° ${s.letra||''} · ${s.turno||''}</span>
        </div>
        <span class="access-item__badge">&#10003;</span>
      </div>`;
  }).join('');
}
fetchHomeStats();

// ════ LOGOUT ════
document.getElementById('logoutBtn')?.addEventListener('click', async () => {
  try { await fetch('/api/admin/logout', { method:'POST' }); } catch (_) {}
  window.location.href = '/';
});

const ADMIN_DRAWER_PASSWORD = '1234';

// ════ MODO KIOSCO / FULLSCREEN ════
const kioskBtn        = document.getElementById('kioskBtn');
const kioskIcon       = document.getElementById('kioskIcon');
const kioskPanel      = document.getElementById('kioskPanel');
const kioskPanelOverlay = document.getElementById('kioskPanelOverlay');
const kioskConfirm    = document.getElementById('kioskConfirm');
const kioskCancel     = document.getElementById('kioskCancel');
const kioskExitFab    = document.getElementById('kioskExitFab');
// ════ ON-SCREEN KEYBOARD (simple-keyboard) ════
const keyboardInputs = 'input[type="text"], input[type="email"], input[type="password"], input[type="number"], input[type="search"], textarea';
let activeInput = null;
let osk = null;
let oskInteracting = false;

let oskLayout = 'default';
let shiftLocked = false;
let lastOskButton = null;
let lastOskButtonAt = 0;
let oskLoading = null;

let kioskActive = false;

// ── Detectar si ya estamos en fullscreen (p.ej. al recargar) ──
function isFullscreen() {
  return !!(
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  );
}

// ── Entrar a fullscreen ──
async function enterFullscreen() {
  const el = document.documentElement;
  try {
    if      (el.requestFullscreen)          await el.requestFullscreen({ navigationUI: 'hide' });
    else if (el.webkitRequestFullscreen)   el.webkitRequestFullscreen();
    else if (el.mozRequestFullScreen)      el.mozRequestFullScreen();
    else if (el.msRequestFullscreen)       el.msRequestFullscreen();
  } catch (e) {
    console.warn('Fullscreen error:', e);
  }
}

// ── Salir de fullscreen ──
async function exitFullscreen() {
  try {
    if      (document.exitFullscreen)          await document.exitFullscreen();
    else if (document.webkitExitFullscreen)   document.webkitExitFullscreen();
    else if (document.mozCancelFullScreen)    document.mozCancelFullScreen();
    else if (document.msExitFullscreen)       document.msExitFullscreen();
  } catch (e) {}
}

// ── Actualizar UI según estado fullscreen ──
function onFullscreenChange() {
  kioskActive = isFullscreen();

  // Ícono del botón topbar
  if (kioskIcon) kioskIcon.textContent = kioskActive ? 'fullscreen_exit' : 'fullscreen';

  // FAB de salida: visible solo en fullscreen
  if (kioskExitFab) {
    if (kioskActive) {
      kioskExitFab.classList.remove('hidden');
      kioskExitFab.classList.add('visible');
    } else {
      kioskExitFab.classList.remove('visible');
      setTimeout(() => kioskExitFab.classList.add('hidden'), 400);
    }
  }

  // Badge en topbar
  document.body.classList.toggle('kiosk-mode', kioskActive);
}

// ── Eventos de cambio fullscreen (cross-browser) ──
document.addEventListener('fullscreenchange',       onFullscreenChange);
document.addEventListener('webkitfullscreenchange', onFullscreenChange);
document.addEventListener('mozfullscreenchange',    onFullscreenChange);
document.addEventListener('MSFullscreenChange',     onFullscreenChange);

// ── Abrir panel de confirmación ──
function openKioskPanel() {
  kioskPanel?.classList.remove('hidden');
  requestAnimationFrame(() => kioskPanel?.classList.add('open'));
}

function closeKioskPanel() {
  kioskPanel?.classList.remove('open');
  setTimeout(() => kioskPanel?.classList.add('hidden'), 280);
}

// Botón topbar → abrir panel (si no está en fullscreen) o salir (si ya está)
kioskBtn?.addEventListener('click', () => {
  if (isFullscreen()) exitFullscreen();
  else                openKioskPanel();
});

// Confirmar → entrar a fullscreen (DEBE ser gesto directo del usuario)
kioskConfirm?.addEventListener('click', async () => {
  closeKioskPanel();
  await new Promise(r => setTimeout(r, 300)); // esperar que cierre el panel
  await enterFullscreen();
});

kioskCancel?.addEventListener('click',        closeKioskPanel);
kioskPanelOverlay?.addEventListener('click',  closeKioskPanel);

// FAB flotante de salida
kioskExitFab?.addEventListener('click', exitFullscreen);

// Tecla Escape ya la maneja el navegador de forma nativa para salir de fullscreen

function showOsk() {
  const el = document.getElementById('osk');
  if (!el) return;
  el.classList.remove('hidden');
  el.setAttribute('aria-hidden', 'false');
}

function hideOsk() {
  const el = document.getElementById('osk');
  if (!el) return;
  el.classList.add('hidden');
  el.setAttribute('aria-hidden', 'true');
}

function setOskLayout(next) {
  if (!osk || oskLayout === next) return;
  oskLayout = next;
  osk.setOptions({ layoutName: oskLayout });
}

function loadSimpleKeyboard() {
  if (window.SimpleKeyboard) return Promise.resolve();
  if (oskLoading) return oskLoading;

  oskLoading = new Promise((resolve, reject) => {
    const jsUrl = 'https://cdn.jsdelivr.net/npm/simple-keyboard@latest/build/index.js';

    if (document.querySelector('script[data-simple-keyboard]')) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = jsUrl;
    script.defer = true;
    script.setAttribute('data-simple-keyboard', '1');
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('simple-keyboard failed to load'));
    document.head.appendChild(script);
  }).catch(() => {});

  return oskLoading;
}

function initOsk() {
  if (osk) return;
  if (!window.SimpleKeyboard) {
    loadSimpleKeyboard().then(() => initOsk());
    return;
  }

  const oskRoot = document.getElementById('osk');
  if (!oskRoot) return;

  oskRoot.addEventListener('pointerdown', e => {
    oskInteracting = true;
    e.preventDefault();
  });
  oskRoot.addEventListener('pointerup', () => {
    setTimeout(() => { oskInteracting = false; }, 0);
  });

  const oskMount = oskRoot.querySelector('.simple-keyboard') || oskRoot;
  osk = new window.SimpleKeyboard.default({
    rootElement: oskMount,
    layoutName: oskLayout,
    onChange: input => {
      if (!activeInput) return;
      activeInput.value = input;
      activeInput.dispatchEvent(new Event('input', { bubbles: true }));
    },
    onKeyPress: button => {
      const now = Date.now();
      if (button === lastOskButton && now - lastOskButtonAt < 120) return;
      lastOskButton = button;
      lastOskButtonAt = now;

      if (button === '{enter}') {
        activeInput?.blur();
        hideOsk();
        return;
      }

      if (button === '{shift}') {
        setOskLayout('shift');
        return;
      }

      if (button === '{lock}') {
        shiftLocked = !shiftLocked;
        setOskLayout(shiftLocked ? 'shift' : 'default');
        return;
      }

      if (!shiftLocked && oskLayout === 'shift') {
        setOskLayout('default');
      }
    },
    layout: {
      default: [
        'q w e r t y u i o p',
        'a s d f g h j k l',
        '{shift} z x c v b n m {bksp}',
        '@ {space} {enter}'
      ],
      shift: [
        'Q W E R T Y U I O P',
        'A S D F G H J K L',
        '{shift} Z X C V B N M {bksp}',
        '@ {space} {enter}'
      ]
    },
    display: {
      '{bksp}': '⌫',
      '{enter}': '↵',
      '{space}': 'espacio',
      '{shift}': '⇧',
      '{lock}': '⇪'
    }
  });
}

document.addEventListener('focusin', e => {
  const target = e.target;
  if (target && target.matches && target.matches(keyboardInputs)) {
    initOsk();
    activeInput = target;
    osk?.setInput(target.value || '');
    showOsk();
  }
});

document.addEventListener('focusout', e => {
  const target = e.target;
  if (target && target.matches && target.matches(keyboardInputs)) {
    setTimeout(() => {
      if (oskInteracting) {
        activeInput?.focus();
        return;
      }
      const focused = document.activeElement;
      if (focused && focused.matches && focused.matches(keyboardInputs)) return;
      activeInput = null;
      hideOsk();
    }, 0);
  }
});

// ════ ACCESO FACIAL ════
let loginLivId       = null;
let loginLivOk       = false;
let loginDeniedCount = 0;
let loginVerifyBusy  = false;
let loginLivBusy     = false;
let loginFaceDetector = null;
let loginFaceTrackId = null;
let loginFaceDetectBusy = false;
let loginFaceLastTick = 0;
let loginFaceLastSeen = 0;
let loginFaceTrackerUsesBrowser = false;

const loginCanvas     = document.getElementById('loginCanvas');
const livDot          = document.getElementById('loginLivenessDot');
const livText         = document.getElementById('loginLivenessText');
const loginScanOverlay = document.getElementById('loginScanOverlay');
const loginScanFrame = loginScanOverlay?.querySelector('.face-scan-frame');

function setLoginScanning(active, box) {
  if (!loginScanOverlay) return;
  loginScanOverlay.classList.toggle('is-visible', active);
  if (!active || !loginScanFrame || !box) return;
  loginScanFrame.style.setProperty('--scan-x', `${Math.round(box.x)}px`);
  loginScanFrame.style.setProperty('--scan-y', `${Math.round(box.y)}px`);
  loginScanFrame.style.setProperty('--scan-w', `${Math.round(box.w)}px`);
  loginScanFrame.style.setProperty('--scan-h', `${Math.round(box.h)}px`);
}

function setLivUi(state, text) {
  if (livText) livText.textContent = text || '';
  if (!livDot) return;
  livDot.style.background =
    state === 'off'        ? '#64748B' :
    state === 'ready'      ? '#006B28' :
    state === 'need_blink' ? '#92400E' : '#006B28';
}

function setLoginReadyUi() {
  if (loginMsg) {
    loginMsg.textContent = t('waiting_face');
    loginMsg.className = 'feedback waiting';
  }
  setLivUi('ready', t('scanning'));
}

function setLoginInactiveUi() {
  setLivUi('off', t('liveness_init'));
}

function _activeCameraSource(videoEl, imgEl) {
  if (videoEl && videoEl.srcObject) return videoEl;
  if (imgEl && !imgEl.classList.contains('hidden')) return imgEl;
  return null;
}

function _sourceDims(el) {
  if (!el) return { w: 0, h: 0 };
  const w = el.videoWidth || el.naturalWidth || el.width || 0;
  const h = el.videoHeight || el.naturalHeight || el.height || 0;
  if (w && h) return { w, h };
  const rect = el.getBoundingClientRect ? el.getBoundingClientRect() : null;
  if (rect && rect.width && rect.height) {
    return { w: Math.round(rect.width), h: Math.round(rect.height) };
  }
  return { w: 0, h: 0 };
}

function _imageReady(el) {
  if (!el || el.tagName !== 'IMG') return true;
  if (!el.complete) return false;
  if (el.naturalWidth && el.naturalHeight) return true;
  const rect = el.getBoundingClientRect ? el.getBoundingClientRect() : null;
  return Boolean(rect && rect.width && rect.height);
}

function _mapFaceBoxToCamera(source, faceBox) {
  const cameraBox = source?.closest?.('.camera-box');
  const rect = cameraBox?.getBoundingClientRect();
  const dims = _sourceDims(source);
  if (!rect || !dims.w || !dims.h || !faceBox) return null;

  const scale = Math.max(rect.width / dims.w, rect.height / dims.h);
  const renderedW = dims.w * scale;
  const renderedH = dims.h * scale;
  const offsetX = (rect.width - renderedW) / 2;
  const offsetY = (rect.height - renderedH) / 2;

  const rawX = faceBox.x * scale + offsetX;
  const rawY = faceBox.y * scale + offsetY;
  const rawW = faceBox.width * scale;
  const rawH = faceBox.height * scale;
  const padX = Math.max(24, rawW * 0.24);
  const padY = Math.max(28, rawH * 0.30);

  const x = Math.max(10, rawX - padX);
  const y = Math.max(10, rawY - padY);
  const w = Math.min(rect.width - x - 10, rawW + padX * 2);
  const h = Math.min(rect.height - y - 10, rawH + padY * 2);
  if (w < 80 || h < 80) return null;
  return { x, y, w, h };
}

function _mapNormalizedFaceBoxToCamera(source, faceBox) {
  const dims = _sourceDims(source);
  if (!dims.w || !dims.h || !faceBox) return null;
  return _mapFaceBoxToCamera(source, {
    x: faceBox.x * dims.w,
    y: faceBox.y * dims.h,
    width: faceBox.width * dims.w,
    height: faceBox.height * dims.h,
  });
}

function updateLoginScanFromServer(faceBox) {
  if (loginFaceTrackerUsesBrowser) return;
  const source = _activeCameraSource(loginVideo, loginImage);
  const box = _mapNormalizedFaceBoxToCamera(source, faceBox);
  if (box) {
    loginFaceLastSeen = performance.now();
    setLoginScanning(true, box);
    return;
  }
  if (!loginFaceLastSeen || performance.now() - loginFaceLastSeen > 900) {
    setLoginScanning(false);
  }
}

function _largestFace(faces) {
  return faces.reduce((best, face) => {
    if (!best) return face;
    const a = face.boundingBox.width * face.boundingBox.height;
    const b = best.boundingBox.width * best.boundingBox.height;
    return a > b ? face : best;
  }, null);
}

function startLoginFaceTracker() {
  stopLoginFaceTracker();
  loginFaceTrackerUsesBrowser = false;
  if (!loginScanOverlay || !('FaceDetector' in window)) {
    setLoginScanning(false);
    return;
  }
  try {
    loginFaceDetector = new FaceDetector({ fastMode: true, maxDetectedFaces: 1 });
    loginFaceTrackerUsesBrowser = true;
  } catch (_) {
    loginFaceDetector = null;
    loginFaceTrackerUsesBrowser = false;
    setLoginScanning(false);
    return;
  }

  const tick = now => {
    if (!loginFaceDetector) return;
    const source = _activeCameraSource(loginVideo, loginImage);
    const dims = _sourceDims(source);
    const ready = source && dims.w && dims.h && (source.tagName !== 'VIDEO' || source.readyState >= 2);

    if (ready && !loginFaceDetectBusy && now - loginFaceLastTick >= 140) {
      loginFaceLastTick = now;
      loginFaceDetectBusy = true;
      loginFaceDetector.detect(source)
        .then(faces => {
          const face = faces?.length ? _largestFace(faces) : null;
          const box = face ? _mapFaceBoxToCamera(source, face.boundingBox) : null;
          if (box) {
            loginFaceLastSeen = performance.now();
            setLoginScanning(true, box);
          }
        })
        .catch(() => {})
        .finally(() => { loginFaceDetectBusy = false; });
    }

    if (!ready || now - loginFaceLastSeen > 650) setLoginScanning(false);
    loginFaceTrackId = requestAnimationFrame(tick);
  };

  loginFaceLastTick = 0;
  loginFaceLastSeen = 0;
  loginFaceTrackId = requestAnimationFrame(tick);
}

function stopLoginFaceTracker() {
  if (loginFaceTrackId) cancelAnimationFrame(loginFaceTrackId);
  loginFaceTrackId = null;
  loginFaceDetector = null;
  loginFaceTrackerUsesBrowser = false;
  loginFaceDetectBusy = false;
  loginFaceLastTick = 0;
  loginFaceLastSeen = 0;
  setLoginScanning(false);
}

function _useMjpeg(imgEl, videoEl) {
  if (videoEl) {
    videoEl.srcObject = null;
    videoEl.classList.add('hidden');
  }
  if (imgEl) {
    imgEl.src = '/api/camera/stream?ts=' + Date.now();
    imgEl.classList.remove('hidden');
  }
}

function _useGetUserMedia(videoEl, imgEl, stream) {
  if (videoEl) {
    videoEl.srcObject = stream;
    videoEl.classList.remove('hidden');
  }
  if (imgEl) {
    imgEl.src = '';
    imgEl.classList.add('hidden');
  }
}

function stopLoginCamera() {
  clearInterval(loginInterval); loginInterval = null;
  if (loginStream && loginStream.getTracks) loginStream.getTracks().forEach(t => t.stop());
  loginStream = null;
  if (loginVideo)  loginVideo.srcObject  = null;
  if (loginImage)  { loginImage.src = ''; loginImage.classList.add('hidden'); }
  if (loginVideo)  loginVideo.classList.remove('hidden');
  if (camOverlay)  camOverlay.classList.remove('hidden');
  if (loginStart)  loginStart.disabled  = false;
  if (loginStop)   loginStop.disabled   = true;
  stopLoginFaceTracker();
  loginLivId = null; loginLivOk = false;
  loginVerifyBusy = false; loginLivBusy = false;
}

// Auto-start: se llama al navegar al view, sin clic manual
async function startLoginCameraAuto() {
  if (loginStream || loginInterval) return;
  if (loginStart) loginStart.disabled = true;
  if (loginStop)  loginStop.disabled  = false;
  setLivUi('init', 'Conectando cámara…');
  try {
    loginLivOk = false; loginLivId = null;
    try {
      const ls = await fetch('/api/login/liveness/start', { method:'POST' });
      const lj = await ls.json();
      if (lj.ok && lj.session_id) loginLivId = lj.session_id;
      else loginLivOk = true;
    } catch (_) { loginLivOk = true; }

    loginStream = await navigator.mediaDevices.getUserMedia({ video: true });
    _useGetUserMedia(loginVideo, loginImage, loginStream);
    if (camOverlay)  camOverlay.classList.add('hidden');
    if (loginMsgHelp) { loginMsgHelp.classList.add('hidden'); loginMsgHelp.classList.remove('is-clickable'); }
    startLoginFaceTracker();
    if (loginMsgHelp) {
      loginMsgHelp.classList.add('hidden');
      loginMsgHelp.classList.remove('is-clickable');
    }
    loginDeniedCount = 0;
    setLoginReadyUi();

    loginInterval = setInterval(async () => {
      if (!loginLivOk) await pushLivFrame();
      else             await captureAndVerify();
    }, 700);
  } catch (_) {
    try {
      loginStream = { backend: 'mjpeg' };
      _useMjpeg(loginImage, loginVideo);
      if (camOverlay)  camOverlay.classList.add('hidden');
      startLoginFaceTracker();
      loginDeniedCount = 0;
      setLoginReadyUi();
      loginInterval = setInterval(async () => {
        if (!loginLivOk) await pushLivFrame();
        else             await captureAndVerify();
      }, 700);
    } catch (_) {
      if (loginMsg) { loginMsg.textContent = t('no_camera'); loginMsg.className = 'feedback denied'; }
      if (loginStart) loginStart.disabled = false;
      if (loginStop)  loginStop.disabled  = true;
    }
  }
}

function showAccessStep(n) {
  const s1 = document.getElementById('access-step1');
  const s2 = document.getElementById('access-step2');
  if (n === 1) { s1?.classList.remove('hidden'); s2?.classList.add('hidden'); }
  else         { s1?.classList.add('hidden');    s2?.classList.remove('hidden'); }
}

async function activateAccessHardware() {
  try {
    const res = await fetch('/api/hardware/access-success', { method: 'POST' });
    const data = await res.json();
    if (!data.ok) {
      console.warn('No se pudo activar el hardware:', data.message || 'error desconocido');
    }
  } catch (error) {
    console.warn('Error al activar el hardware:', error);
  }
}

async function pushLivFrame() {
  if (loginLivBusy) return;
  if (!loginCanvas || !loginLivId) return;
  loginLivBusy = true;
  try {
    const useLatest = loginStream && loginStream.backend === 'mjpeg';
    let body = { session_id: loginLivId };
    if (useLatest) {
      body.use_latest = true;
    } else {
      const source = _activeCameraSource(loginVideo, loginImage);
      if (!source) return;
      if (!_imageReady(source)) return;
      const dims = _sourceDims(source);
      if (!dims.w || !dims.h) return;
      loginCanvas.width  = dims.w;
      loginCanvas.height = dims.h;
      try {
        loginCanvas.getContext('2d').drawImage(source, 0, 0, dims.w, dims.h);
      } catch (_) {
        loginLivBusy = false;
        return;
      }
      body.image = loginCanvas.toDataURL('image/jpeg', 0.75);
    }
    const res  = await fetch('/api/login/liveness/frame', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body),
    });
    const data = await res.json();
    updateLoginScanFromServer(data.face_box);
    setLivUi(data.state, data.message);
    if (data.state === 'ready') {
      loginLivOk = true;
      if (loginMsg) { loginMsg.textContent = 'Identificando…'; loginMsg.className = 'feedback waiting'; }
    }
  } catch (err) {
    console.error("Error en pushLivFrame:", err);
  } finally {
    loginLivBusy = false;
  }
}

async function captureAndVerify() {
  if (loginVerifyBusy) return;
  if (!loginCanvas) return;
  loginVerifyBusy = true;
  try {
    const useLatest = loginStream && loginStream.backend === 'mjpeg';
    let body = { liveness_session_id: loginLivId };
    if (useLatest) {
      body.use_latest = true;
    } else {
      const source = _activeCameraSource(loginVideo, loginImage);
      if (!source) return;
      if (!_imageReady(source)) return;
      const dims = _sourceDims(source);
      if (!dims.w || !dims.h) return;
      loginCanvas.width  = dims.w;
      loginCanvas.height = dims.h;
      try {
        loginCanvas.getContext('2d').drawImage(source, 0, 0, dims.w, dims.h);
      } catch (_) {
        loginVerifyBusy = false;
        return;
      }
      body.image = loginCanvas.toDataURL('image/jpeg', 0.8);
    }
    const res  = await fetch('/api/login/verify', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body),
    });
    const data = await res.json();
    updateLoginScanFromServer(data.face_box);
    if (data.state === 'granted' || data.state === 'denied') {
      stopLoginFaceTracker();
    }
    if (loginMsg) { loginMsg.textContent = data.message||''; loginMsg.className = 'feedback '+(data.state||''); }
    if (data.state === 'granted') {
      stopLoginCamera();
      renderAccessResult(data);
      showAccessStep(2);
      activateAccessHardware();
      if (loginMsgHelp) { loginMsgHelp.classList.add('hidden'); loginMsgHelp.classList.remove('is-clickable'); }
      loginDeniedCount = 0;
    }
    if (data.state === 'denied') {
      loginDeniedCount += 1;
      if (loginMsgHelp) {
        loginMsgHelp.classList.remove('hidden');
        if (loginDeniedCount >= 3) loginMsgHelp.classList.add('is-clickable');
      }
    }
  } catch (err) {
    console.error("Error en captureAndVerify:", err);
  } finally {
    loginVerifyBusy = false;
  }
}

loginStart?.addEventListener('click', async () => {
  try {
    showAccessStep(1);
    loginLivOk = false; loginLivId = null;
    setLivUi('init', 'Conectando…');

    try {
      const ls = await fetch('/api/login/liveness/start', { method:'POST' });
      const lj = await ls.json();
      if (lj.ok && lj.session_id) loginLivId = lj.session_id;
      else loginLivOk = true;
    } catch (_) { loginLivOk = true; }

    loginStream = await navigator.mediaDevices.getUserMedia({ video: true });
    _useGetUserMedia(loginVideo, loginImage, loginStream);
    if (camOverlay)  camOverlay.classList.add('hidden');
    if (loginStart)  loginStart.disabled  = true;
    if (loginStop)   loginStop.disabled   = false;
    startLoginFaceTracker();
    if (loginStart)  loginStart.disabled   = true;
    if (loginStop)   loginStop.disabled    = false;
    if (loginMsgHelp) { loginMsgHelp.classList.add('hidden'); loginMsgHelp.classList.remove('is-clickable'); }
    loginDeniedCount = 0;
    setLoginReadyUi();

    loginInterval = setInterval(async () => {
      if (!loginLivOk) await pushLivFrame();
      else             await captureAndVerify();
    }, 700);
  } catch (_) {
    try {
      loginStream = { backend: 'mjpeg' };
      _useMjpeg(loginImage, loginVideo);
      if (camOverlay)  camOverlay.classList.add('hidden');
      if (loginStart)  loginStart.disabled  = true;
      if (loginStop)   loginStop.disabled   = false;
      loginDeniedCount = 0;
      setLoginReadyUi();
      loginInterval = setInterval(async () => {
        if (!loginLivOk) await pushLivFrame();
        else             await captureAndVerify();
      }, 700);
    } catch (_) {
      if (loginMsg) { loginMsg.textContent = t('no_camera'); loginMsg.className = 'feedback denied'; }
    }
  }
});

loginStop?.addEventListener('click', () => {
  stopLoginCamera();
  setLoginInactiveUi();
  if (loginMsg) { loginMsg.textContent = t('waiting_face'); loginMsg.className = 'feedback waiting'; }
  if (loginMsgHelp) { loginMsgHelp.classList.add('hidden'); loginMsgHelp.classList.remove('is-clickable'); }
  loginDeniedCount = 0;
});

function renderAccessResult(data) {
  const cont = document.getElementById('accessResult');
  if (!cont) return;
  const granted = data.state === 'granted';
  const now     = new Date().toLocaleTimeString('es-MX', { hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:true });
  const u       = data.user || {};
  cont.innerHTML = `
    <div class="result-banner result-banner--${granted ? 'granted':'denied'}">
      <span class="result-banner__icon material-symbols-outlined">${granted ? 'check_circle':'cancel'}</span>
      <div>
        <div>${granted ? 'Acceso concedido' : 'Acceso denegado'}</div>
        <div class="result-banner__time">Registro: ${now}</div>
      </div>
    </div>
    ${granted ? `
    <div class="credential-card">
      <div class="credential-card__photo">
        ${u.foto_url
          ? `<img class="credential-card__img" src="${u.foto_url}?t=${Date.now()}" alt="Foto">`
          : `<div class="credential-card__ph">Sin foto</div>`}
      </div>
      <div class="credential-card__meta">
        <div class="credential-card__title">Credencial</div>
        <p><strong>Nombre</strong> ${u.nombre||'---'}</p>
        <p><strong>Grado</strong>  ${u.grado||u.salon||'---'}</p>
        <p><strong>Grupo</strong>  ${u.letra||u.grupo||'---'}</p>
        <p><strong>Turno</strong>  ${u.turno||'---'}</p>
        <p><strong>ID</strong>     ${u.id != null ? '#'+u.id : '---'}</p>
      </div>
    </div>` : `
    <div class="feedback denied">${data.message || 'Rostro no reconocido.'}</div>`}`;
}

function resetAccessStep() {
  showAccessStep(1);
  stopLoginCamera();
  setLoginInactiveUi();
  if (loginMsg) { loginMsg.textContent = t('waiting_face'); loginMsg.className = 'feedback waiting'; }
  if (loginMsgHelp) { loginMsgHelp.classList.add('hidden'); loginMsgHelp.classList.remove('is-clickable'); }
  loginDeniedCount = 0;
}

document.getElementById('btnScanAnother')?.addEventListener('click', resetAccessStep);

function openLoginHelpModal()  { loginHelpModal?.classList.remove('hidden'); }
function closeLoginHelpModal() { loginHelpModal?.classList.add('hidden'); }
loginMsgHelp?.addEventListener('click', () => { if (loginMsgHelp?.classList.contains('is-clickable')) openLoginHelpModal(); });
loginHelpOverlay?.addEventListener('click', closeLoginHelpModal);
loginHelpClose?.addEventListener('click', closeLoginHelpModal);

// ════ REGISTRO BIOMÉTRICO ════
let regImages    = { image_front: null, image_left: null, image_right: null };
let regDatos     = { nombre:'', grado:'1', letra:'', turno:'MATUTINO' };

const regCanvas  = document.getElementById('regCanvas');

const regNombreInput = document.getElementById('regNombre');
regNombreInput?.addEventListener('input', () => {
  const raw = regNombreInput.value;
  const cleaned = raw.replace(/[^A-Za-zÁÉÍÓÚÑáéíóúñ\s]/g, '').replace(/\s{2,}/g, ' ');
  const limited = cleaned.slice(0, 80);
  if (limited !== raw) regNombreInput.value = limited;
});

const REG_ANGLES = [
  { key:'image_front', guide:'perfilHead_frente.png', get label(){ return t('btn_capture_front'); }, get hint(){ return t('angle_hint_front'); } },
  { key:'image_left',  guide:'perfilHead_izquierdo.png', get label(){ return t('btn_capture_left');  }, get hint(){ return t('angle_hint_left');  } },
  { key:'image_right', guide:'perfilHead_derecho.png', get label(){ return t('btn_save_student');  }, get hint(){ return t('angle_hint_right'); } },
];

const REG_GUIDE_CACHE = new Map();
function preloadRegGuides() {
  REG_ANGLES.forEach(angle => {
    const src = `/static/img/guides/${angle.guide}`;
    if (REG_GUIDE_CACHE.has(src)) return;
    const img = new Image();
    img.src = src;
    REG_GUIDE_CACHE.set(src, img);
  });
}
preloadRegGuides();

function updateRegAngleUi() {
  document.querySelectorAll('.angle-step').forEach((el, i) => {
    el.classList.remove('angle-step--active','angle-step--done');
    const numEl = el.querySelector('.angle-step__num');
    if (i < regStepIndex)        { el.classList.add('angle-step--done');   if (numEl) numEl.textContent = '✓'; }
    else if (i === regStepIndex) { el.classList.add('angle-step--active'); if (numEl) numEl.textContent = i+1; }
    else                         { if (numEl) numEl.textContent = i+1; }
  });
  const hint  = document.getElementById('regAngleHint');
  const label = document.getElementById('regCaptureLabel');
  const guide = document.getElementById('regAngleGuideImg');
  const angle = REG_ANGLES[regStepIndex];
  if (hint  && angle) hint.textContent  = angle.hint;
  if (label && angle) label.textContent = angle.label;

  if (guide && angle) {
    const src = `/static/img/guides/${angle.guide}`;
    guide.src = src;
  }
}

function stopRegCamera() {
  if (regStream && regStream.getTracks) regStream.getTracks().forEach(t => t.stop());
  regStream = null;
  if (regVideo)   regVideo.srcObject  = null;
  if (regImage)   { regImage.src = ''; regImage.classList.add('hidden'); }
  if (regVideo)   regVideo.classList.remove('hidden');
  if (regStart)   regStart.disabled   = false;
  if (regCapture) regCapture.disabled = true;
  if (regStop)    regStop.disabled    = true;
  if (regCamOv)   regCamOv.classList.remove('hidden');
}

document.getElementById('regGoToCamera')?.addEventListener('click', () => {
  const nombreRaw = document.getElementById('regNombre')?.value || '';
  const nombre = nombreRaw.trim().replace(/[^A-Za-zÁÉÍÓÚÑáéíóúñ\s]/g, '');
  const grado  = document.getElementById('regGrado')?.value;
  const letra  = document.getElementById('regLetra')?.value.trim().toUpperCase();
  const turno  = document.getElementById('regTurno')?.value;
  const msg1   = document.getElementById('regStep1Msg');

  if (!nombre) { if (msg1) { msg1.textContent = 'Ingresa el nombre.'; msg1.className='feedback denied'; } return; }
  if (!letra)  { if (msg1) { msg1.textContent = 'Ingresa el grupo.';  msg1.className='feedback denied'; } return; }
  if (!nombre || !letra) {
    if (msg1) {
      msg1.textContent = 'Completa los campos faltantes para continuar.';
      msg1.className='feedback denied';
    }
    return;
  }

  if (nombre.length < 3 || nombre.length > 20) {
    if (msg1) {
      msg1.textContent = 'El nombre debe tener entre 3 y 20 caracteres.';
      msg1.className='feedback denied';
    }
    return;
  }

  if (nombre !== nombreRaw.trim()) {
    const input = document.getElementById('regNombre');
    if (input) input.value = nombre;
  }

  regDatos = { nombre, grado, letra, turno };
  regStepIndex = 0;
  regImages    = { image_front:null, image_left:null, image_right:null };

  document.getElementById('reg-step1')?.classList.add('hidden');
  document.getElementById('reg-step2')?.classList.remove('hidden');
  updateRegAngleUi();
});

document.getElementById('btnBackToStep1')?.addEventListener('click', () => {
  stopRegCamera();
  regStepIndex = 0;
  regImages    = { image_front:null, image_left:null, image_right:null };
  document.getElementById('reg-step2')?.classList.add('hidden');
  document.getElementById('reg-step1')?.classList.remove('hidden');
});

regStart?.addEventListener('click', async () => {
  try {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error('getUserMedia not available');
    regStream = await navigator.mediaDevices.getUserMedia({ video: true });
    _useGetUserMedia(regVideo, regImage, regStream);
    if (regCamOv)   regCamOv.classList.add('hidden');
    if (regStart)   regStart.disabled   = true;
    if (regCapture) regCapture.disabled = false;
    if (regStop)    regStop.disabled    = false;
    if (regMsg)     { regMsg.textContent = t('reg_cam_ready'); regMsg.className = 'feedback waiting'; }
  } catch (_) {
    try {
      regStream = { backend: 'mjpeg' };
      _useMjpeg(regImage, regVideo);
      if (regCamOv)   regCamOv.classList.add('hidden');
      if (regStart)   regStart.disabled   = true;
      if (regCapture) regCapture.disabled = false;
      if (regStop)    regStop.disabled    = false;
      if (regMsg)     { regMsg.textContent = t('reg_cam_ready'); regMsg.className = 'feedback waiting'; }
    } catch (_) {
      if (regMsg) { regMsg.textContent = t('no_camera'); regMsg.className = 'feedback denied'; }
    }
  }
});

regCapture?.addEventListener('click', async () => {
  if (!regCanvas) return;
  const source = _activeCameraSource(regVideo, regImage);
  if (!source) return;
  const dims = _sourceDims(source);
  if (!dims.w || !dims.h) return;
  regCanvas.width  = dims.w;
  regCanvas.height = dims.h;
  regCanvas.getContext('2d').drawImage(source, 0, 0, dims.w, dims.h);
  const image = regCanvas.toDataURL('image/jpeg', 0.88);
  const angle = REG_ANGLES[regStepIndex];
  regImages[angle.key] = image;

  if (regStepIndex < 2) {
    regStepIndex++;
    updateRegAngleUi();
    if (regMsg) { regMsg.textContent = t('reg_saved_angle'); regMsg.className = 'feedback waiting'; }
    return;
  }

  if (regMsg) { regMsg.textContent = 'Enviando…'; regMsg.className = 'feedback waiting'; }
  try {
    const res  = await fetch('/api/registro', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ ...regDatos, ...regImages }),
    });
    const data = await res.json();
    if (regMsg) { regMsg.textContent = data.message || (data.ok ? t('reg_success') : t('reg_error')); regMsg.className = 'feedback '+(data.ok?'granted':'denied'); }
    if (data.ok) {
      stopRegCamera();
      setTimeout(() => {
        regStepIndex = 0;
        regImages    = { image_front:null, image_left:null, image_right:null };
        document.getElementById('reg-step2')?.classList.add('hidden');
        document.getElementById('reg-step1')?.classList.remove('hidden');
        const n = document.getElementById('regNombre');
        const l = document.getElementById('regLetra');
        if (n) n.value = ''; if (l) l.value = '';
        const m = document.getElementById('regStep1Msg');
        if (m) { m.textContent = '¡Registrado!'; m.className = 'feedback granted'; }
      }, 2000);
    }
  } catch (_) {
    if (regMsg) { regMsg.textContent = t('reg_conn_error'); regMsg.className = 'feedback denied'; }
  }
});

regStop?.addEventListener('click', stopRegCamera);
updateRegAngleUi();

// ════ CAMBIO A REGISTRO DE ADMIN ════
document.getElementById('btnSwitchToAdminReg')?.addEventListener('click', () => {
  const pass = prompt('Ingresa la contraseña de administrador para continuar:');
  if (pass === ADMIN_DRAWER_PASSWORD) {
    showView('register-admin');
  } else if (pass !== null) {
    alert('Contraseña incorrecta');
  }
});

// ════ REGISTRO ADMIN ════
let regAdminDatos = {};
let regAdminImages = { image_front:null, image_left:null, image_right:null };

const regAdminCanvas = document.getElementById('regAdminCanvas');

function updateRegAdminAngleUi() {
  document.querySelectorAll('#regAdminStepper .angle-step').forEach((el, i) => {
    el.classList.remove('angle-step--active','angle-step--done');
    const numEl = el.querySelector('.angle-step__num');
    if (i < regAdminStepIndex)        { el.classList.add('angle-step--done');   if (numEl) numEl.textContent = '✓'; }
    else if (i === regAdminStepIndex) { el.classList.add('angle-step--active'); if (numEl) numEl.textContent = i+1; }
    else                         { if (numEl) numEl.textContent = i+1; }
  });
  const hint  = document.getElementById('regAdminAngleHint');
  const label = document.getElementById('regAdminCaptureLabel');
  const angle = REG_ANGLES[regAdminStepIndex];
  if (hint  && angle) hint.textContent  = angle.hint;
  if (label && angle) label.textContent = angle.label;
}

function stopRegAdminCamera() {
  if (regAdminStream && regAdminStream.getTracks) regAdminStream.getTracks().forEach(t => t.stop());
  regAdminStream = null;
  if (regAdminVideo)   regAdminVideo.srcObject  = null;
  if (regAdminImage)   { regAdminImage.src = ''; regAdminImage.classList.add('hidden'); }
  if (regAdminVideo)   regAdminVideo.classList.remove('hidden');
  if (regAdminStart)   regAdminStart.disabled   = false;
  if (regAdminCapture) regAdminCapture.disabled = true;
  if (regAdminStop)    regAdminStop.disabled    = true;
  if (regAdminCamOv)   regAdminCamOv.classList.remove('hidden');
}

document.getElementById('regAdminGoToCamera')?.addEventListener('click', () => {
  const num_empleado = document.getElementById('regAdminNum')?.value || '';
  const nombreRaw = document.getElementById('regAdminNombre')?.value || '';
  const nombre = nombreRaw.trim().replace(/[^A-Za-zÁÉÍÓÚÑáéíóúñ\s]/g, '');
  const rol = document.getElementById('regAdminRol')?.value || 'ADMIN';
  const correo = document.getElementById('regAdminCorreo')?.value.trim().toLowerCase() || '';
  const password = document.getElementById('regAdminPass')?.value || '';
  const msg1 = document.getElementById('regAdminStep1Msg');

  if (!num_empleado || !nombre || !correo || !password) {
    if (msg1) {
      msg1.textContent = 'Completa los campos faltantes para continuar.';
      msg1.className='feedback denied';
    }
    return;
  }

  if (nombre.length < 3 || nombre.length > 20) {
    if (msg1) {
      msg1.textContent = 'El nombre debe tener entre 3 y 20 caracteres.';
      msg1.className='feedback denied';
    }
    return;
  }

  if (!_isEmail(correo)) {
    if (msg1) { msg1.textContent='Correo invalido.'; msg1.className='feedback denied'; }
    return;
  }

  regAdminDatos = { num_empleado, nombre, rol, correo, password };
  regAdminStepIndex = 0;
  regAdminImages    = { image_front:null, image_left:null, image_right:null };

  document.getElementById('reg-admin-step1')?.classList.add('hidden');
  document.getElementById('reg-admin-step2')?.classList.remove('hidden');
  updateRegAdminAngleUi();
});

document.getElementById('btnBackToAdminStep1')?.addEventListener('click', () => {
  stopRegAdminCamera();
  document.getElementById('reg-admin-step2')?.classList.add('hidden');
  document.getElementById('reg-admin-step1')?.classList.remove('hidden');
});

document.getElementById('regAdminCancel')?.addEventListener('click', () => {
  showView('register');
});

regAdminStart?.addEventListener('click', async () => {
  try {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error('getUserMedia not available');
    }
    regAdminStream = await navigator.mediaDevices.getUserMedia({ video: true });
    _useGetUserMedia(regAdminVideo, regAdminImage, regAdminStream);
    if (regAdminCamOv)   regAdminCamOv.classList.add('hidden');
    if (regAdminStart)   regAdminStart.disabled   = true;
    if (regAdminCapture) regAdminCapture.disabled = false;
    if (regAdminStop)    regAdminStop.disabled    = false;
    if (regAdminMsg)     { regAdminMsg.textContent = t('reg_cam_ready'); regAdminMsg.className = 'feedback waiting'; }
  } catch (_) {
    try {
      regAdminStream = { backend: 'mjpeg' };
      _useMjpeg(regAdminImage, regAdminVideo);
      if (regAdminCamOv)   regAdminCamOv.classList.add('hidden');
      if (regAdminStart)   regAdminStart.disabled   = true;
      if (regAdminCapture) regAdminCapture.disabled = false;
      if (regAdminStop)    regAdminStop.disabled    = false;
      if (regAdminMsg)     { regAdminMsg.textContent = t('reg_cam_ready'); regAdminMsg.className = 'feedback waiting'; }
    } catch (_) {
      if (regAdminMsg) { regAdminMsg.textContent = t('no_camera'); regAdminMsg.className = 'feedback denied'; }
    }
  }
});

regAdminCapture?.addEventListener('click', async () => {
  if (!regAdminCanvas) return;
  const source = _activeCameraSource(regAdminVideo, regAdminImage);
  if (!source) return;
  const dims = _sourceDims(source);
  if (!dims.w || !dims.h) return;
  regAdminCanvas.width  = dims.w;
  regAdminCanvas.height = dims.h;
  regAdminCanvas.getContext('2d').drawImage(source, 0, 0, dims.w, dims.h);
  const image = regAdminCanvas.toDataURL('image/jpeg', 0.88);
  const angle = REG_ANGLES[regAdminStepIndex];
  regAdminImages[angle.key] = image;

  if (regAdminStepIndex < 2) {
    regAdminStepIndex++;
    updateRegAdminAngleUi();
    if (regAdminMsg) { regAdminMsg.textContent = t('reg_saved_angle'); regAdminMsg.className = 'feedback waiting'; }
    return;
  }

  if (regAdminMsg) { regAdminMsg.textContent = 'Enviando…'; regAdminMsg.className = 'feedback waiting'; }
  try {
    const res  = await fetch('/api/registro-admin', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ ...regAdminDatos, ...regAdminImages }),
    });
    const data = await res.json();
    if (regAdminMsg) { regAdminMsg.textContent = data.message || (data.ok ? t('reg_success') : t('reg_error')); regAdminMsg.className = 'feedback '+(data.ok?'granted':'denied'); }
    if (data.ok) {
      stopRegAdminCamera();
      setTimeout(() => {
        regAdminStepIndex = 0;
        regAdminImages    = { image_front:null, image_left:null, image_right:null };
        document.getElementById('reg-admin-step2')?.classList.add('hidden');
        document.getElementById('reg-admin-step1')?.classList.remove('hidden');
        document.getElementById('regAdminNum').value = '';
        document.getElementById('regAdminNombre').value = '';
        document.getElementById('regAdminCorreo').value = '';
        document.getElementById('regAdminPass').value = '';
        const m = document.getElementById('regAdminStep1Msg');
        if (m) { m.textContent = '¡Administrador Registrado!'; m.className = 'feedback granted'; }
      }, 2000);
    }
  } catch (_) {
    if (regAdminMsg) { regAdminMsg.textContent = t('reg_conn_error'); regAdminMsg.className = 'feedback denied'; }
  }
});

regAdminStop?.addEventListener('click', stopRegAdminCamera);


// ════ ADMIN TABS ════
document.querySelectorAll('.tab-btn[data-admin-tab]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn[data-admin-tab]').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.admin-tab').forEach(t => t.classList.add('hidden'));
    btn.classList.add('active');
    document.getElementById('admin-' + btn.dataset.adminTab)?.classList.remove('hidden');

    const tab = btn.dataset.adminTab;
    if (tab === 'students') loadStudents();
    if (tab === 'admins') loadAdmins();
    if (tab === 'logs') loadAdminAccessLogs();
    if (tab === 'dashboard') loadDashboard();
    if (tab === 'hardware') loadServoSettings();
  });
});

// Click por defecto en el primer tab de admin ('home') al abrir app, o al abrir view admin
const btnAdminHome = document.querySelector('.tab-btn[data-admin-tab="home"]');
if (btnAdminHome) btnAdminHome.classList.add('active');
const adminHomeTab = document.getElementById('admin-home');
if (adminHomeTab) adminHomeTab.classList.remove('hidden');

function _dashInitials(value) {
  const raw = String(value || '').trim();
  if (!raw) return '--';
  const parts = raw.split(/\s+/).filter(Boolean);
  const letters = parts.slice(0, 2).map(p => p[0]?.toUpperCase() || '');
  return letters.join('') || '--';
}

function _renderDashList(container, items) {
  if (!container) return;
  container.innerHTML = items.join('');
}

function _sanitizeName(raw) {
  const cleaned = String(raw || '').replace(/[^A-Za-zÁÉÍÓÚÑáéíóúñ\s]/g, '').replace(/\s{2,}/g, ' ');
  return cleaned.trim();
}

function _sanitizeGroup(raw) {
  const cleaned = String(raw || '').replace(/[^A-Za-z]/g, '').toUpperCase();
  return cleaned.slice(0, 1);
}

function _sanitizeEmployee(raw) {
  return String(raw || '').replace(/\D/g, '').slice(0, 12);
}

function _sanitizeRole(raw) {
  return String(raw || '').replace(/[^A-Za-z_]/g, '').toUpperCase().slice(0, 20);
}

function _isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || '').trim());
}

const dashStudentsCache = new Map();
const dashAdminsCache = new Map();

async function loadDashboardStudents() {
  const listEl = document.getElementById('dashStudents');
  const msgEl = document.getElementById('dashStudentsMsg');
  if (!listEl) return;
  try {
    const res = await fetch('/api/admin/students');
    const data = await res.json();
    const list = (data.students || []).filter(s => s.estado_activo !== 0);
    dashStudentsCache.clear();
    list.forEach(s => dashStudentsCache.set(Number(s.id), s));
    const items = list.map(s => {
      const name = s.nombre || '---';
      const grupo = s.grupo || s.letra || '---';
      const turno = s.turno || '---';
      const grado = s.grado || '---';
      const initials = _dashInitials(name);
      const img = `/api/credencial/${s.id}?t=${Date.now()}`;
      return `
        <div class="dash-person" data-type="student" data-id="${s.id}">
          <div class="dash-person__photo">
            <img src="${img}" alt="${name}" onload="this.nextElementSibling?.classList.add('hidden')" onerror="this.remove()">
            <span class="dash-person__initials">${initials}</span>
          </div>
          <div class="dash-person__meta">
            <div class="dash-person__name">${name}</div>
            <div class="dash-person__sub">${grado}${grupo} · ${turno}</div>
          </div>
          <div class="dash-actions">
            <button class="dash-action-btn" data-action="photo">Foto</button>
            <button class="dash-action-btn" data-action="edit">Editar</button>
            <button class="dash-action-btn dash-action-btn--danger" data-action="delete">Eliminar</button>
          </div>
        </div>`;
    });
    _renderDashList(listEl, items);
    if (msgEl) { msgEl.textContent = `${list.length} ${t('dash_students').toLowerCase()}.`; msgEl.className = 'feedback waiting'; }
  } catch (_) {
    if (msgEl) { msgEl.textContent = 'Error al cargar.'; msgEl.className = 'feedback denied'; }
  }
}

async function loadDashboardAdmins() {
  const listEl = document.getElementById('dashAdmins');
  const msgEl = document.getElementById('dashAdminsMsg');
  if (!listEl) return;
  try {
    const res = await fetch('/api/admin/admins');
    const data = await res.json();
    const list = (data.admins || []).filter(a => a.estado_activo !== 0);
    dashAdminsCache.clear();
    list.forEach(a => dashAdminsCache.set(Number(a.id), a));
    const items = list.map(a => {
      const name = a.nombre_completo || a.nombre || '---';
      const rol = a.rol || 'ADMIN';
      const correo = a.correo || '---';
      const initials = _dashInitials(name);
      return `
        <div class="dash-person" data-type="admin" data-id="${a.id}">
          <div class="dash-person__photo">
            <span class="dash-person__initials">${initials}</span>
          </div>
          <div class="dash-person__meta">
            <div class="dash-person__name">${name}</div>
            <div class="dash-person__sub">${rol} · ${correo}</div>
          </div>
          <div class="dash-actions">
            <button class="dash-action-btn" data-action="edit">Editar</button>
            <button class="dash-action-btn dash-action-btn--danger" data-action="delete">Eliminar</button>
          </div>
        </div>`;
    });
    _renderDashList(listEl, items);
    if (msgEl) { msgEl.textContent = `${list.length} ${t('dash_admins').toLowerCase()}.`; msgEl.className = 'feedback waiting'; }
  } catch (_) {
    if (msgEl) { msgEl.textContent = 'Error al cargar.'; msgEl.className = 'feedback denied'; }
  }
}

async function loadDashboardLogs() {
  const tbody = document.querySelector('#accessLogsTable tbody');
  const msgEl = document.getElementById('dashLogsMsg');
  if (!tbody) return;
  try {
    const sessionRes = await fetch('/api/admin/access-session');
    const sessionData = await sessionRes.json();
    if (!sessionData.active) {
      tbody.innerHTML = '';
      if (msgEl) { msgEl.textContent = t('dash_no_session'); msgEl.className = 'feedback denied'; }
      return;
    }

    const res = await fetch('/api/admin/access-logs/active-session?limit=50');
    const data = await res.json();
    const list = data.logs || [];
    const filtered = list.filter(l => (l.tipo_usuario || 'ESTUDIANTE') === 'ESTUDIANTE');
    tbody.innerHTML = filtered.map(l => {
      const time = l.fecha_hora || '--';
      const name = l.nombre_usuario || '--';
      const event = l.tipo_evento || '--';
      const result = l.acceso_concedido ? 'OK' : 'DENEGADO';
      return `<tr><td>${time}</td><td>${name}</td><td>${event}</td><td>${result}</td></tr>`;
    }).join('');

    if (msgEl) {
      msgEl.textContent = filtered.length ? `${filtered.length} ${t('dash_access_logs').toLowerCase()}.` : t('dash_no_logs');
      msgEl.className = 'feedback waiting';
    }
  } catch (_) {
    if (msgEl) { msgEl.textContent = 'Error al cargar.'; msgEl.className = 'feedback denied'; }
  }
}

function loadDashboard() {
  loadDashboardStudents();
  loadDashboardAdmins();
  loadDashboardLogs();
}

document.getElementById('dashRefreshStudents')?.addEventListener('click', loadDashboardStudents);
document.getElementById('dashRefreshAdmins')?.addEventListener('click', loadDashboardAdmins);
document.getElementById('dashRefreshLogs')?.addEventListener('click', loadDashboardLogs);

const dashPhotoModal = document.getElementById('dashPhotoModal');
const dashPhotoTitle = document.getElementById('dashPhotoTitle');
const dashPhotoImg = document.getElementById('dashPhotoImg');
const dashPhotoMeta = document.getElementById('dashPhotoMeta');
const dashPhotoFallback = document.getElementById('dashPhotoFallback');

function openDashPhotoModal(student) {
  if (!dashPhotoModal || !dashPhotoImg) return;
  const name = student?.nombre || '---';
  const grupo = student?.grupo || student?.letra || '---';
  const turno = student?.turno || '---';
  const grado = student?.grado || '---';
  const photoUrl = student?.foto_url || student?.foto || `/api/credencial/${student.id}`;
  if (dashPhotoTitle) dashPhotoTitle.textContent = t('dash_photo_title');
  if (dashPhotoMeta) dashPhotoMeta.textContent = `${name} · ${grado}${grupo} · ${turno}`;
  if (dashPhotoFallback) dashPhotoFallback.classList.add('hidden');
  dashPhotoImg.onload = () => {
    if (dashPhotoFallback) dashPhotoFallback.classList.add('hidden');
  };
  dashPhotoImg.onerror = () => {
    if (dashPhotoFallback) dashPhotoFallback.classList.remove('hidden');
  };
  dashPhotoImg.src = `${photoUrl}?t=${Date.now()}`;
  dashPhotoModal.classList.remove('hidden');
}

function closeDashPhotoModal() {
  dashPhotoModal?.classList.add('hidden');
  if (dashPhotoImg) dashPhotoImg.src = '';
}

document.getElementById('dashPhotoClose')?.addEventListener('click', closeDashPhotoModal);
dashPhotoModal?.addEventListener('click', e => { if (e.target === dashPhotoModal) closeDashPhotoModal(); });

const dashCrudModal = document.getElementById('dashCrudModal');
const dashCrudTitle = document.getElementById('dashCrudTitle');
const dashCrudMsg = document.getElementById('dashCrudMsg');
const dashCrudStudentFields = document.getElementById('dashCrudStudentFields');
const dashCrudAdminFields = document.getElementById('dashCrudAdminFields');

let dashCrudState = { type: 'student', mode: 'create', id: null };

document.getElementById('dashStudentNombre')?.addEventListener('input', e => {
  e.target.value = _sanitizeName(e.target.value).slice(0, 60);
});
document.getElementById('dashStudentGrupo')?.addEventListener('input', e => {
  e.target.value = _sanitizeGroup(e.target.value);
});
document.getElementById('dashAdminNum')?.addEventListener('input', e => {
  e.target.value = _sanitizeEmployee(e.target.value);
});
document.getElementById('dashAdminNombre')?.addEventListener('input', e => {
  e.target.value = _sanitizeName(e.target.value).slice(0, 40);
});
document.getElementById('dashAdminRol')?.addEventListener('input', e => {
  e.target.value = _sanitizeRole(e.target.value);
});

function openDashCrudModal(type, mode, data) {
  dashCrudState = { type, mode, id: data?.id || null };
  if (!dashCrudModal || !dashCrudTitle) return;
  dashCrudTitle.textContent = mode === 'create' ? `${t('dash_create')} ${type === 'student' ? t('dash_students') : t('dash_admins')}` : `Editar ${type === 'student' ? t('dash_students') : t('dash_admins')}`;
  if (dashCrudMsg) dashCrudMsg.style.display = 'none';

  if (dashCrudStudentFields && dashCrudAdminFields) {
    dashCrudStudentFields.classList.toggle('hidden', type !== 'student');
    dashCrudAdminFields.classList.toggle('hidden', type !== 'admin');
  }

  if (type === 'student') {
    document.getElementById('dashStudentNombre').value = data?.nombre || '';
    document.getElementById('dashStudentGrado').value = data?.grado || '1';
    document.getElementById('dashStudentGrupo').value = data?.grupo || data?.letra || '';
    document.getElementById('dashStudentTurno').value = data?.turno || 'MATUTINO';
    document.getElementById('dashStudentActivo').value = data?.estado_activo != null ? String(data.estado_activo) : '1';
  }

  if (type === 'admin') {
    document.getElementById('dashAdminNum').value = data?.numero_empleado || data?.num_empleado || '';
    document.getElementById('dashAdminNombre').value = data?.nombre_completo || data?.nombre || '';
    document.getElementById('dashAdminRol').value = data?.rol || 'ADMIN';
    document.getElementById('dashAdminCorreo').value = data?.correo || '';
    document.getElementById('dashAdminPass').value = '';
    document.getElementById('dashAdminActivo').value = data?.estado_activo != null ? String(data.estado_activo) : '1';
  }

  dashCrudModal.classList.remove('hidden');
}

function closeDashCrudModal() {
  dashCrudModal?.classList.add('hidden');
}

document.getElementById('dashCrudCancel')?.addEventListener('click', e => {
  e.preventDefault();
  closeDashCrudModal();
});

dashCrudModal?.addEventListener('click', e => { if (e.target === dashCrudModal) closeDashCrudModal(); });

async function saveDashCrud() {
  if (!dashCrudMsg) return;
  dashCrudMsg.style.display = '';
  dashCrudMsg.textContent = 'Guardando...';
  dashCrudMsg.className = 'feedback waiting';

  try {
    if (dashCrudState.type === 'student') {
      const payload = {
        nombre: _sanitizeName(document.getElementById('dashStudentNombre').value),
        grado: document.getElementById('dashStudentGrado').value,
        grupo: _sanitizeGroup(document.getElementById('dashStudentGrupo').value),
        turno: document.getElementById('dashStudentTurno').value,
        estado_activo: parseInt(document.getElementById('dashStudentActivo').value, 10),
      };
      if (!payload.nombre || payload.nombre.length < 3) throw new Error('Nombre invalido.');
      if (!payload.grupo) throw new Error('Grupo invalido.');

      if (dashCrudState.mode === 'create') {
        const res = await fetch('/api/admin/students', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) throw new Error(data.message || 'Error');
      } else {
        const res = await fetch(`/api/admin/students/${dashCrudState.id}`, {
          method: 'PUT', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) throw new Error(data.message || 'Error');
      }

      await loadDashboardStudents();
      closeDashCrudModal();
      return;
    }

    if (dashCrudState.type === 'admin') {
      const payload = {
        numero_empleado: _sanitizeEmployee(document.getElementById('dashAdminNum').value),
        nombre: _sanitizeName(document.getElementById('dashAdminNombre').value),
        rol: _sanitizeRole(document.getElementById('dashAdminRol').value),
        correo: document.getElementById('dashAdminCorreo').value.trim().toLowerCase(),
        password: document.getElementById('dashAdminPass').value,
        estado_activo: parseInt(document.getElementById('dashAdminActivo').value, 10),
      };
      if (!payload.numero_empleado) throw new Error('No. empleado invalido.');
      if (!payload.nombre || payload.nombre.length < 3) throw new Error('Nombre invalido.');
      if (!_isEmail(payload.correo)) throw new Error('Correo invalido.');

      if (dashCrudState.mode === 'create') {
        if (!payload.password || payload.password.length < 6) throw new Error('Password invalido.');
        const res = await fetch('/api/admin/admins', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) throw new Error(data.message || 'Error');
      } else {
        if (!payload.password) delete payload.password;
        const res = await fetch(`/api/admin/admins/${dashCrudState.id}`, {
          method: 'PUT', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.ok) throw new Error(data.message || 'Error');
      }

      await loadDashboardAdmins();
      closeDashCrudModal();
      return;
    }
  } catch (err) {
    dashCrudMsg.textContent = err?.message || 'Error.';
    dashCrudMsg.className = 'feedback denied';
  }
}

document.getElementById('dashCrudSave')?.addEventListener('click', e => {
  e.preventDefault();
  saveDashCrud();
});

document.getElementById('dashCreateStudent')?.addEventListener('click', () => openDashCrudModal('student', 'create'));
document.getElementById('dashCreateAdmin')?.addEventListener('click', () => openDashCrudModal('admin', 'create'));

document.getElementById('dashStudents')?.addEventListener('click', e => {
  const actionBtn = e.target.closest('[data-action]');
  const card = e.target.closest('.dash-person');
  if (!card) return;
  const id = Number(card.dataset.id);
  const student = dashStudentsCache.get(id);
  if (!student) return;

  if (actionBtn) {
    const action = actionBtn.dataset.action;
    if (action === 'photo') openDashPhotoModal(student);
    if (action === 'edit') openDashCrudModal('student', 'edit', student);
    if (action === 'delete') deleteDashStudent(id);
    return;
  }

  openDashPhotoModal(student);
});

document.getElementById('dashAdmins')?.addEventListener('click', e => {
  const actionBtn = e.target.closest('[data-action]');
  const card = e.target.closest('.dash-person');
  if (!card) return;
  const id = Number(card.dataset.id);
  const admin = dashAdminsCache.get(id);
  if (!admin) return;

  if (actionBtn) {
    const action = actionBtn.dataset.action;
    if (action === 'edit') openDashCrudModal('admin', 'edit', admin);
    if (action === 'delete') deleteDashAdmin(id);
    return;
  }

  openDashCrudModal('admin', 'edit', admin);
});

async function deleteDashStudent(id) {
  if (!confirm(`¿Eliminar estudiante #${id}?`)) return;
  try {
    const res = await fetch(`/api/admin/students/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (!data.ok) throw new Error(data.message || 'Error');
    loadDashboardStudents();
  } catch (err) {
    const msgEl = document.getElementById('dashStudentsMsg');
    if (msgEl) { msgEl.textContent = err?.message || 'Error al eliminar.'; msgEl.className = 'feedback denied'; }
  }
}

async function deleteDashAdmin(id) {
  if (!confirm(`¿Eliminar administrador #${id}?`)) return;
  try {
    const res = await fetch(`/api/admin/admins/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (!data.ok) throw new Error(data.message || 'Error');
    loadDashboardAdmins();
  } catch (err) {
    const msgEl = document.getElementById('dashAdminsMsg');
    if (msgEl) { msgEl.textContent = err?.message || 'Error al eliminar.'; msgEl.className = 'feedback denied'; }
  }
}

const servoHoldInput = document.getElementById('servoHoldSeconds');
const servoAlwaysInput = document.getElementById('servoAlwaysActive');
const servoMsg = document.getElementById('servoMsg');

async function loadServoSettings() {
  if (!servoHoldInput || !servoAlwaysInput) return;
  try {
    const res = await fetch('/api/admin/servo-settings');
    const data = await res.json();
    const cfg = data.config || {};
    if (cfg.hold_seconds != null) servoHoldInput.value = cfg.hold_seconds;
    servoAlwaysInput.value = cfg.always_active ? 'true' : 'false';
    if (servoMsg) { servoMsg.textContent = 'Configuracion cargada.'; servoMsg.className = 'feedback granted'; }
  } catch (_) {
    if (servoMsg) { servoMsg.textContent = 'Error al cargar.'; servoMsg.className = 'feedback denied'; }
  }
}

async function saveServoSettings() {
  if (!servoHoldInput || !servoAlwaysInput) return;
  try {
    const res = await fetch('/api/admin/servo-settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        hold_seconds: parseFloat(servoHoldInput.value),
        always_active: servoAlwaysInput.value === 'true',
      }),
    });
    const data = await res.json();
    if (servoMsg) { servoMsg.textContent = data.message || (data.ok ? 'Guardado.' : 'Error'); servoMsg.className = 'feedback ' + (data.ok ? 'granted' : 'denied'); }
  } catch (_) {
    if (servoMsg) { servoMsg.textContent = 'Error al guardar.'; servoMsg.className = 'feedback denied'; }
  }
}

document.getElementById('servoLoad')?.addEventListener('click', loadServoSettings);
document.getElementById('servoSave')?.addEventListener('click', saveServoSettings);

// ════ ADMIN: LOGS ════
const logTurno = document.getElementById('logTurno');
const logGrado = document.getElementById('logGrado');
const logGrupo = document.getElementById('logGrupo');
const logEvento = document.getElementById('logEvento');
const logResultado = document.getElementById('logResultado');
const logNombre = document.getElementById('logNombre');

function _formatLogEvent(value) {
  const raw = String(value || '').trim().toLowerCase();
  if (!raw) return '--';
  if (raw === 'entrada') return t('log_event_entry');
  if (raw === 'salida') return t('log_event_exit');
  return value;
}

function _formatLogResult(value) {
  return value ? t('log_result_ok') : t('log_result_denied');
}

async function loadAdminAccessLogs() {
  const tbody = document.querySelector('#adminAccessLogsTable tbody');
  const msg = document.getElementById('adminLogsMsg');
  if (!tbody) return;

  const params = new URLSearchParams();
  params.set('limit', '10');

  const turno = logTurno?.value || '';
  const grado = logGrado?.value || '';
  const grupo = _sanitizeGroup(logGrupo?.value);
  const evento = logEvento?.value || '';
  const resultado = logResultado?.value || '';
  const nombre = _sanitizeName(logNombre?.value);

  if (turno) params.set('turno', turno);
  if (grado) params.set('grado', grado);
  if (grupo) params.set('grupo', grupo);
  if (evento) params.set('tipo_evento', evento);
  if (resultado) params.set('acceso_concedido', resultado);
  if (nombre) params.set('nombre', nombre);

  if (logGrupo && grupo) logGrupo.value = grupo;
  if (logNombre && nombre) logNombre.value = nombre;

  try {
    const res = await fetch(`/api/admin/access-logs?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.message || 'Error');

    const list = data.logs || [];
    tbody.innerHTML = list.map(l => {
      const time = l.fecha_hora || '--';
      const name = l.nombre_usuario || '--';
      const gradoVal = l.grado || '--';
      const grupoVal = l.grupo || '--';
      const turnoVal = l.turno || '--';
      const event = _formatLogEvent(l.tipo_evento || '--');
      const result = _formatLogResult(l.acceso_concedido);
      return `
        <tr>
          <td>${time}</td>
          <td>${name}</td>
          <td>${gradoVal}</td>
          <td>${grupoVal}</td>
          <td>${turnoVal}</td>
          <td>${event}</td>
          <td>${result}</td>
        </tr>`;
    }).join('');

    if (msg) {
      msg.textContent = list.length
        ? `${list.length} ${t('dash_access_logs').toLowerCase()}.`
        : t('log_no_records');
      msg.className = 'feedback waiting';
    }
  } catch (err) {
    if (msg) {
      msg.textContent = err?.message || 'Error al cargar.';
      msg.className = 'feedback denied';
    }
  }
}

document.getElementById('logSearch')?.addEventListener('click', loadAdminAccessLogs);
document.getElementById('logClear')?.addEventListener('click', () => {
  if (logTurno) logTurno.value = '';
  if (logGrado) logGrado.value = '';
  if (logGrupo) logGrupo.value = '';
  if (logEvento) logEvento.value = '';
  if (logResultado) logResultado.value = '';
  if (logNombre) logNombre.value = '';
  loadAdminAccessLogs();
});

// ════ ADMIN: ESTUDIANTES ════
const studentsCache = new Map();

async function loadStudents() {
  const tbody = document.querySelector('#studentsTable tbody');
  const msg   = document.getElementById('admStudentsMsg');
  if (!tbody) return;
  try {
    const res  = await fetch('/api/admin/students');
    const data = await res.json();
    const list = data.students || data || [];
    studentsCache.clear();
    list.forEach(s => studentsCache.set(Number(s.id), s));
    tbody.innerHTML = list.map(s => `
      <tr>
        <td>${s.id}</td><td>${s.nombre}</td><td>${s.grado}</td>
        <td>${s.letra||s.grupo||'---'}</td><td>${s.turno}</td>
        <td style="text-align:center">${s.estado_activo !== 0 ? '&#10003;':'&#10007;'}</td>
        <td style="display:flex;gap:6px;flex-wrap:wrap">
          <button style="padding:4px 9px;font-size:.72rem;box-shadow:none;background:var(--primary)"
            type="button" onclick="openStudentPhoto(${s.id})">Foto</button>
          <button style="padding:4px 9px;font-size:.72rem;box-shadow:none;background:#B91C1C"
            onclick="deleteStudent(${s.id})">Eliminar</button>
        </td>
      </tr>`).join('');
    if (msg) { msg.textContent = `${list.length} estudiantes.`; msg.className = 'feedback waiting'; }
  } catch (_) { if (msg) { msg.textContent = 'Error al cargar.'; msg.className = 'feedback denied'; } }
}

window.openStudentPhoto = id => {
  const student = studentsCache.get(Number(id));
  if (student) openDashPhotoModal(student);
};

window.deleteStudent = async id => {
  if (!confirm(`¿Eliminar estudiante #${id}?`)) return;
  const msg = document.getElementById('admStudentsMsg');
  try {
    const res = await fetch(`/api/admin/students/${id}`, { method:'DELETE' });
    const data = await res.json();
    if (!data.ok) throw new Error(data.message || 'Error');
    loadStudents();
  } catch (err) {
    if (msg) { msg.textContent = err?.message || 'Error al eliminar.'; msg.className = 'feedback denied'; }
  }
};

document.getElementById('admRefresh')?.addEventListener('click', loadStudents);

document.getElementById('admCreate')?.addEventListener('click', async () => {
  const msg    = document.getElementById('admStudentsMsg');
  const nombre = _sanitizeName(document.getElementById('admNombre')?.value);
  const grado  = document.getElementById('admGrado')?.value;
  const grupo  = _sanitizeGroup(document.getElementById('admGrupo')?.value);
  const turno  = document.getElementById('admTurno')?.value;
  if (!nombre || nombre.length < 3) { if (msg) { msg.textContent='Nombre invalido.'; msg.className='feedback denied'; } return; }
  if (!grupo) { if (msg) { msg.textContent='Grupo invalido.'; msg.className='feedback denied'; } return; }
  try {
    const res  = await fetch('/api/admin/students', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ nombre, grado, grupo, turno }),
    });
    const data = await res.json();
    if (msg) { msg.textContent = data.message||(data.ok?'Creado.':'Error'); msg.className='feedback '+(data.ok?'granted':'denied'); }
    if (data.ok) loadStudents();
  } catch (_) { if (msg) { msg.textContent='Error.'; msg.className='feedback denied'; } }
});

// ════ ADMIN: MODELO ════
document.getElementById('cfgLoad')?.addEventListener('click', async () => {
  const msg = document.getElementById('cfgMsg');
  try {
    const res  = await fetch('/api/admin/model-config');
    const data = await res.json();
    const cfg = data.config || {};
    if (cfg.scale != null)               document.getElementById('cfgScale').value     = cfg.scale;
    if (cfg.tolerance != null)           document.getElementById('cfgTolerance').value = cfg.tolerance;
    if (cfg.cooldown_seconds != null)    document.getElementById('cfgCooldown').value  = cfg.cooldown_seconds;
    if (msg) { msg.textContent='Configuración cargada.'; msg.className='feedback granted'; }
    updateModelTestValues();
  } catch (_) {}
});

document.getElementById('cfgSave')?.addEventListener('click', async () => {
  const msg = document.getElementById('cfgMsg');
  try {
    const res  = await fetch('/api/admin/model-config', {
      method:'PUT', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        scale:            parseFloat(document.getElementById('cfgScale')?.value),
        tolerance:        parseFloat(document.getElementById('cfgTolerance')?.value),
        cooldown_seconds: parseFloat(document.getElementById('cfgCooldown')?.value),
      }),
    });
    const data = await res.json();
    if (msg) { msg.textContent = data.message||(data.ok?'Guardado.':'Error'); msg.className='feedback '+(data.ok?'granted':'denied'); }
    if (data.ok) updateModelTestValues();
  } catch (_) {}
});

// ════ ADMIN: PRUEBA MODELO ════
let modelTestStream  = null;
const modelTestModal   = document.getElementById('modelTestModal');
const modelTestOverlay = document.getElementById('modelTestOverlay');
const modelTestClose   = document.getElementById('modelTestClose');
const modelTestVideo   = document.getElementById('modelTestVideo');
const modelTestCanvas  = document.getElementById('modelTestCanvas');
const modelTestFps     = document.getElementById('modelTestFps');
const modelTestFaces   = document.getElementById('modelTestFaces');
const modelTestScale   = document.getElementById('modelTestScale');
const modelTestTol     = document.getElementById('modelTestTolerance');
const modelTestCool    = document.getElementById('modelTestCooldown');
let modelTestDetector  = null;
let modelTestAnimId    = null;
let modelTestFrames    = 0;
let modelTestLastTick  = 0;

function updateModelTestValues() {
  const scale     = document.getElementById('cfgScale')?.value;
  const tolerance = document.getElementById('cfgTolerance')?.value;
  const cooldown  = document.getElementById('cfgCooldown')?.value;
  if (modelTestScale) modelTestScale.textContent = scale     || '--';
  if (modelTestTol)   modelTestTol.textContent   = tolerance || '--';
  if (modelTestCool)  modelTestCool.textContent  = cooldown  || '--';
}

async function openModelTest() {
  if (!modelTestModal) return;
  updateModelTestValues();
  modelTestModal.classList.remove('hidden');
  try {
    modelTestStream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (modelTestVideo) modelTestVideo.srcObject = modelTestStream;
    modelTestDetector = ('FaceDetector' in window)
      ? new FaceDetector({ fastMode: true, maxDetectedFaces: 3 })
      : null;
    modelTestFrames   = 0;
    modelTestLastTick = performance.now();
    startModelTestLoop();
  } catch (_) {}
}

function closeModelTest() {
  if (modelTestModal) modelTestModal.classList.add('hidden');
  if (modelTestAnimId) cancelAnimationFrame(modelTestAnimId);
  modelTestAnimId = null;
  if (modelTestStream) modelTestStream.getTracks().forEach(t => t.stop());
  modelTestStream = null;
  if (modelTestVideo) modelTestVideo.srcObject = null;
  if (modelTestCanvas) modelTestCanvas.getContext('2d')?.clearRect(0, 0, modelTestCanvas.width, modelTestCanvas.height);
  if (modelTestFps)   modelTestFps.textContent   = '--';
  if (modelTestFaces) modelTestFaces.textContent = '--';
}

async function startModelTestLoop() {
  if (!modelTestVideo || !modelTestCanvas) return;
  const ctx = modelTestCanvas.getContext('2d');
  const loop = async () => {
    if (!modelTestModal || modelTestModal.classList.contains('hidden')) return;
    if (modelTestVideo.readyState < 2) { modelTestAnimId = requestAnimationFrame(loop); return; }

    modelTestCanvas.width  = modelTestVideo.videoWidth;
    modelTestCanvas.height = modelTestVideo.videoHeight;
    ctx?.clearRect(0, 0, modelTestCanvas.width, modelTestCanvas.height);

    let facesCount = 0;
    if (modelTestDetector && ctx) {
      try {
        const faces = await modelTestDetector.detect(modelTestVideo);
        facesCount = faces.length;
        ctx.lineWidth = 3;
        ctx.strokeStyle = 'rgba(0,255,140,.9)';
        ctx.fillStyle   = 'rgba(0,255,140,.12)';
        faces.forEach(face => {
          const b = face.boundingBox;
          ctx.strokeRect(b.x, b.y, b.width, b.height);
          ctx.fillRect(b.x, b.y, b.width, b.height);
        });
      } catch (_) { facesCount = 0; }
    }

    modelTestFrames += 1;
    const now     = performance.now();
    const elapsed = now - modelTestLastTick;
    if (elapsed >= 500) {
      const fps = Math.round((modelTestFrames / elapsed) * 1000);
      if (modelTestFps)   modelTestFps.textContent   = String(fps);
      if (modelTestFaces) modelTestFaces.textContent = String(facesCount);
      modelTestFrames   = 0;
      modelTestLastTick = now;
    }
    modelTestAnimId = requestAnimationFrame(loop);
  };
  modelTestAnimId = requestAnimationFrame(loop);
}

document.getElementById('cfgTest')?.addEventListener('click', openModelTest);
modelTestOverlay?.addEventListener('click', closeModelTest);
modelTestClose?.addEventListener('click',   closeModelTest);

// ════ ADMIN: ADMINS ════
async function loadAdmins() {
  const tbody = document.querySelector('#adminsTable tbody');
  const msg   = document.getElementById('adminMsg');
  if (!tbody) return;
  try {
    const res  = await fetch('/api/admin/admins');
    const data = await res.json();
    const list = data.admins || data || [];
    tbody.innerHTML = list.map(a => `
      <tr>
        <td>${a.id}</td><td>${a.numero_empleado || a.num_empleado || '---'}</td><td>${a.nombre || a.nombre_completo || '---'}</td>
        <td>${a.rol || 'ADMIN'}</td><td>${a.correo||'---'}</td>
        <td style="text-align:center">${a.estado_activo !== 0 ? '&#10003;':'&#10007;'}</td>
      </tr>`).join('');
    if (msg) { msg.textContent=`${list.length} administradores.`; msg.className='feedback waiting'; }
  } catch (_) {}
}

document.getElementById('adminRefresh')?.addEventListener('click', loadAdmins);

document.getElementById('adminCreate')?.addEventListener('click', async () => {
  const msg  = document.getElementById('adminMsg');
  const body = {
    numero_empleado: _sanitizeEmployee(document.getElementById('adminNum')?.value),
    nombre:          _sanitizeName(document.getElementById('adminNombre')?.value),
    rol:             _sanitizeRole(document.getElementById('adminRol')?.value),
    correo:          document.getElementById('adminCorreo')?.value.trim().toLowerCase(),
    password:        document.getElementById('adminPass')?.value,
  };
  if (!body.numero_empleado || !body.nombre || !body.password) {
    if (msg) { msg.textContent='Completa los campos obligatorios.'; msg.className='feedback denied'; }
    return;
  }
  if (!_isEmail(body.correo)) {
    if (msg) { msg.textContent='Correo invalido.'; msg.className='feedback denied'; }
    return;
  }
  try {
    const res  = await fetch('/api/admin/admins', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (msg) { msg.textContent = data.message||(data.ok?'Admin creado.':'Error'); msg.className='feedback '+(data.ok?'granted':'denied'); }
    if (data.ok) loadAdmins();
  } catch (_) { if (msg) { msg.textContent='Error.'; msg.className='feedback denied'; } }
});

// ════ INIT ════
applyLang(currentLang);
