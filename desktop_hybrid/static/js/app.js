/* ═══════════════════════════════════════════════════════════════════════
   VerifyMe · app.js
═══════════════════════════════════════════════════════════════════════ */

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
    tab_students:'Estudiantes', tab_model:'Modelo', tab_admins:'Admins',
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
    tab_students:'Students', tab_model:'Model', tab_admins:'Admins',
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

function openDrawer()  {
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
document.getElementById('drawerClose')?.addEventListener('click', closeDrawer);
drawerOverlay?.addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeDrawer(); closeClockOverlay(); }
});

// ════ NAVEGACIÓN ════
const allViews = document.querySelectorAll('.view');
const navBtns  = document.querySelectorAll('.nav-btn[data-view]');

function showView(viewId) {
  if (viewId !== 'access')   stopLoginCamera();
  if (viewId !== 'register') stopRegCamera();

  allViews.forEach(v => v.classList.add('hidden'));
  navBtns.forEach(b => b.classList.remove('active'));

  const target = document.getElementById('view-' + viewId);
  if (target) target.classList.remove('hidden');

  const btn = document.querySelector('.nav-btn[data-view="' + viewId + '"]');
  if (btn) btn.classList.add('active');

  const titleEl = document.getElementById('topbarTitle');
  if (titleEl) titleEl.textContent = t('title_' + viewId) || viewId;

  closeDrawer();

  if (viewId === 'access') startLoginCamera();
}

navBtns.forEach(b => b.addEventListener('click', () => showView(b.dataset.view)));

document.querySelectorAll('.quick-nav-btn[data-goto]').forEach(b => {
  b.addEventListener('click', () => showView(b.dataset.goto));
});

const urlView = new URLSearchParams(window.location.search).get('view');
if (urlView && ['home','access','register','admin'].includes(urlView)) {
  showView(urlView);
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

// ── Tiempos configurables ──
const INACTIVITY_MS  = 60000; // 60s inactivo → inicia cuenta regresiva
const COUNTDOWN_SECS = 10;    // 10s de cuenta regresiva visible

// ── Toast elementos ──
const clockToast    = document.getElementById('clockToast');
const toastNum      = document.getElementById('toastNum');
const toastProgress = document.getElementById('toastProgress');
const toastCancel   = document.getElementById('toastCancel');
const toastMsg      = document.getElementById('toastMsg');

// Circunferencia del SVG circle r=13 → 2π×13 ≈ 81.68 ≈ 82
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

// ── Mostrar overlay con transición suave ──
function openClockOverlay() {
  if (!clockOverlay) return;
  stopCountdown();
  stopInactivityTimer();
  hideToast();
  clockOverlay.classList.remove('hidden');
  // Forzar reflow para que la transición CSS funcione
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
  // Esperar a que termine la transición antes de ocultar
  setTimeout(() => {
    if (!clockOverlay.classList.contains('visible')) {
      clockOverlay.classList.add('hidden');
    }
  }, 650);
  resetInactivityTimer();
}

// ── Toast cuenta regresiva ──
function showToast() {
  if (!clockToast) return;
  let secs = COUNTDOWN_SECS;
  toastNum.textContent = secs;
  // Barra arranca llena y va vaciando
  toastProgress.style.strokeDashoffset = 0;
  clockToast.classList.add('visible');

  countdownInterval = setInterval(() => {
    secs--;
    if (toastNum) toastNum.textContent = secs;
    // Progreso: va de 0 a CIRC conforme bajan los segundos
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
    // Primero muestra el toast con cuenta regresiva
    showToast();
  }, INACTIVITY_MS);
}

function stopInactivityTimer() {
  clearTimeout(inactivityTimer);
  inactivityTimer = null;
  stopCountdown();
}

// Cancelar con el botón del toast
toastCancel?.addEventListener('click', e => {
  e.stopPropagation();
  stopCountdown();
  resetInactivityTimer();
});

// Reiniciar timer con cualquier actividad (solo cuando overlay está oculto)
['click','touchstart','mousemove','keydown','scroll','pointerdown'].forEach(ev => {
  document.addEventListener(ev, () => {
    if (!clockOverlay?.classList.contains('visible')) {
      // Si el toast está visible, ocultarlo y reiniciar
      if (clockToast?.classList.contains('visible')) {
        stopCountdown();
        resetInactivityTimer();
        return;
      }
      resetInactivityTimer();
    }
  }, { passive: true });
});

// Tocar cualquier parte del overlay lo cierra
clockOverlay?.addEventListener('click', closeClockOverlay);

// Botón reloj en topbar
document.getElementById('clockModeBtn')?.addEventListener('click', e => {
  e.stopPropagation();
  openClockOverlay();
});

// Arrancar en modo reloj al cargar (sin cuenta regresiva, directo)
openClockOverlay();

// ════ HOME STATS ════
async function fetchHomeStats() {
  try {
    const res  = await fetch('/api/admin/students');
    const data = await res.json();
    const list = data.students || data || [];
    const tot  = document.getElementById('statTotal');
    const act  = document.getElementById('statActivos');
    if (tot) tot.textContent = list.length;
    if (act) act.textContent = list.filter(s => s.activo !== false).length;
  } catch (_) {}
}
fetchHomeStats();

// ════ LOGOUT ════
document.getElementById('logoutBtn')?.addEventListener('click', async () => {
  try { await fetch('/api/admin/logout', { method:'POST' }); } catch (_) {}
  window.location.href = '/';
});

// ════ ON-SCREEN KEYBOARD (simple-keyboard) ════
const keyboardInputs = 'input[type="text"], input[type="email"], input[type="password"], input[type="number"], input[type="adminValidateNombre"],input[type="adminValidateCorreo"],input[type="adminValidatePass"], textarea';
let activeInput = null;
let osk = null;
let oskInteracting = false;

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

function initOsk() {
  if (osk || !window.SimpleKeyboard) return;
  const oskRoot = document.getElementById('osk');
  oskRoot?.addEventListener('pointerdown', e => {
    oskInteracting = true;
    e.preventDefault();
  });
  oskRoot?.addEventListener('pointerup', () => {
    setTimeout(() => { oskInteracting = false; }, 0);
  });
  osk = new window.SimpleKeyboard.default({
    onChange: input => {
      if (!activeInput) return;
      activeInput.value = input;
      activeInput.dispatchEvent(new Event('input', { bubbles: true }));
    },
    onKeyPress: button => {
      if (button === '{enter}') {
        activeInput?.blur();
        hideOsk();
      }
      if (button === '{shift}' || button === '{lock}') handleShift();
    },
    layout: {
      default: [
        'q w e r t y u i o p',
        'a s d f g h j k l',
        '{shift} z x c v b n m {bksp}',
        '{space} {enter}'
      ],
      shift: [
        'Q W E R T Y U I O P',
        'A S D F G H J K L',
        '{shift} Z X C V B N M {bksp}',
        '{space} {enter}'
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

function handleShift() {
  if (!osk) return;
  const current = osk.options.layoutName || 'default';
  const next = current === 'default' ? 'shift' : 'default';
  osk.setOptions({ layoutName: next });
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
let loginStream      = null;
let loginInterval    = null;
let loginLivId       = null;
let loginLivOk       = false;
let loginDeniedCount = 0;

const loginVideo      = document.getElementById('loginVideo');
const loginImage      = document.getElementById('loginImage');
const loginCanvas     = document.getElementById('loginCanvas');
const loginStart      = document.getElementById('loginStart');
const loginStop       = document.getElementById('loginStop');
const loginMsg        = document.getElementById('loginMessage');
const loginMsgHelp    = document.getElementById('loginMessageHelp');
const loginHelpModal  = document.getElementById('loginHelpModal');
const loginHelpOverlay= document.getElementById('loginHelpOverlay');
const loginHelpClose  = document.getElementById('loginHelpClose');
const camOverlay      = document.getElementById('cameraOverlay');
const livDot          = document.getElementById('loginLivenessDot');
const livText         = document.getElementById('loginLivenessText');

function setLivUi(state, text) {
  if (livText) livText.textContent = text || '';
  if (!livDot) return;
  livDot.style.background =
    state === 'ready'      ? '#006B28' :
    state === 'need_blink' ? '#92400E' : '#006B28';
}

function _activeCameraSource(videoEl, imgEl) {
  if (videoEl && videoEl.srcObject) return videoEl;
  if (imgEl && !imgEl.classList.contains('hidden')) return imgEl;
  return null;
}

function _sourceDims(el) {
  const w = el?.videoWidth || el?.naturalWidth || el?.width || 0;
  const h = el?.videoHeight || el?.naturalHeight || el?.height || 0;
  return { w, h };
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
  loginLivId = null; loginLivOk = false;
}

function showAccessStep(n) {
  const s1 = document.getElementById('access-step1');
  const s2 = document.getElementById('access-step2');
  if (n === 1) { s1?.classList.remove('hidden'); s2?.classList.add('hidden'); }
  else         { s1?.classList.add('hidden');    s2?.classList.remove('hidden'); }
}

async function startLoginCamera() {
  if (loginStream || loginInterval) return;
  try {
    showAccessStep(1);
    loginLivOk = false; loginLivId = null;
    setLivUi('init', t('liveness_init'));

    try {
      const ls = await fetch('/api/login/liveness/start', { method:'POST' });
      const lj = await ls.json();
      if (lj.ok && lj.session_id) {
        loginLivId = lj.session_id;
      } else {
        loginLivOk = true;
      }
    } catch (_) { loginLivOk = true; }

    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error('getUserMedia not available');
    }
    loginStream = await navigator.mediaDevices.getUserMedia({ video: true });
    _useGetUserMedia(loginVideo, loginImage, loginStream);
    if (camOverlay)  camOverlay.classList.add('hidden');
    if (loginMsgHelp) {
      loginMsgHelp.classList.add('hidden');
      loginMsgHelp.classList.remove('is-clickable');
    }
    loginDeniedCount = 0;

    loginInterval = setInterval(async () => {
      if (!loginLivOk) await pushLivFrame();
      else             await captureAndVerify();
    }, 700);
  } catch (_) {
    try {
      loginStream = { backend: 'mjpeg' };
      _useMjpeg(loginImage, loginVideo);
      if (camOverlay)  camOverlay.classList.add('hidden');
      loginDeniedCount = 0;
      loginInterval = setInterval(async () => {
        if (!loginLivOk) await pushLivFrame();
        else             await captureAndVerify();
      }, 700);
    } catch (_) {
      if (loginMsg) { loginMsg.textContent = t('no_camera'); loginMsg.className = 'feedback denied'; }
    }
  }
}

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
  setLivUi('init', t('liveness_init'));
  if (loginMsg) { loginMsg.textContent = t('waiting_face'); loginMsg.className = 'feedback waiting'; }
  if (loginMsgHelp) { loginMsgHelp.classList.add('hidden'); loginMsgHelp.classList.remove('is-clickable'); }
  loginDeniedCount = 0;
}

document.getElementById('btnScanAnother')?.addEventListener('click', resetAccessStep);

async function pushLivFrame() {
  if (!loginCanvas || !loginLivId) return;
  const source = _activeCameraSource(loginVideo, loginImage);
  if (!source) return;
  const dims = _sourceDims(source);
  if (!dims.w || !dims.h) return;
  loginCanvas.width  = dims.w;
  loginCanvas.height = dims.h;
  loginCanvas.getContext('2d').drawImage(source, 0, 0, dims.w, dims.h);
  const image = loginCanvas.toDataURL('image/jpeg', 0.75);
  try {
    const res  = await fetch('/api/login/liveness/frame', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ session_id: loginLivId, image }),
    });
    const data = await res.json();
    setLivUi(data.state, data.message);
    if (data.state === 'ready') {
      loginLivOk = true;
      if (loginMsg) { loginMsg.textContent = 'Identificando…'; loginMsg.className = 'feedback waiting'; }
    }
  } catch (_) {}
}

async function captureAndVerify() {
  if (!loginCanvas) return;
  const source = _activeCameraSource(loginVideo, loginImage);
  if (!source) return;
  const dims = _sourceDims(source);
  if (!dims.w || !dims.h) return;
  loginCanvas.width  = dims.w;
  loginCanvas.height = dims.h;
  loginCanvas.getContext('2d').drawImage(source, 0, 0, dims.w, dims.h);
  const image = loginCanvas.toDataURL('image/jpeg', 0.8);
  try {
    const res  = await fetch('/api/login/verify', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ image, liveness_session_id: loginLivId }),
    });
    const data = await res.json();
    if (loginMsg) { loginMsg.textContent = data.message||''; loginMsg.className = 'feedback '+(data.state||''); }
    if (data.state === 'granted') {
      stopLoginCamera();
      renderAccessResult(data);
      showAccessStep(2);
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
  } catch (_) {}
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
    if (loginVideo)  loginVideo.srcObject  = loginStream;
    if (camOverlay)  camOverlay.classList.add('hidden');
    if (loginStart)  loginStart.disabled   = true;
    if (loginStop)   loginStop.disabled    = false;
    if (loginMsgHelp) { loginMsgHelp.classList.add('hidden'); loginMsgHelp.classList.remove('is-clickable'); }
    loginDeniedCount = 0;

    loginInterval = setInterval(async () => {
      if (!loginLivOk) await pushLivFrame();
      else             await captureAndVerify();
    }, 700);
  } catch (_) {
    if (loginMsg) { loginMsg.textContent = t('no_camera'); loginMsg.className = 'feedback denied'; }
  }
});

loginStop?.addEventListener('click', () => {
  stopLoginCamera();
  setLivUi('off', 'Verificación detenida.');
  if (loginMsg) { loginMsg.textContent = t('waiting_face'); loginMsg.className = 'feedback waiting'; }
  if (loginMsgHelp) { loginMsgHelp.classList.add('hidden'); loginMsgHelp.classList.remove('is-clickable'); }
  loginDeniedCount = 0;
});

function openLoginHelpModal()  { loginHelpModal?.classList.remove('hidden'); }
function closeLoginHelpModal() { loginHelpModal?.classList.add('hidden'); }
loginMsgHelp?.addEventListener('click', () => { if (loginMsgHelp?.classList.contains('is-clickable')) openLoginHelpModal(); });
loginHelpOverlay?.addEventListener('click', closeLoginHelpModal);
loginHelpClose?.addEventListener('click', closeLoginHelpModal);

// ════ REGISTRO BIOMÉTRICO ════
let regStream    = null;
let regStepIndex = 0;
let regImages    = { image_front: null, image_left: null, image_right: null };
let regDatos     = { nombre:'', grado:'1', letra:'', turno:'MATUTINO' };

const regVideo   = document.getElementById('regVideo');
const regImage   = document.getElementById('regImage');
const regCanvas  = document.getElementById('regCanvas');
const regStart   = document.getElementById('regStart');
const regCapture = document.getElementById('regCapture');
const regStop    = document.getElementById('regStop');
const regMsg     = document.getElementById('regMessage');
const regCamOv   = document.getElementById('regCameraOverlay');

const regNombreInput = document.getElementById('regNombre');
regNombreInput?.addEventListener('input', () => {
  const raw = regNombreInput.value;
  const cleaned = raw.replace(/[^A-Za-zÁÉÍÓÚÑáéíóúñ\s]/g, '').replace(/\s{2,}/g, ' ');
  const limited = cleaned.slice(0, 20);
  if (limited !== raw) regNombreInput.value = limited;
});

const REG_ANGLES = [
  { key:'image_front', get label(){ return t('btn_capture_front'); }, get hint(){ return t('angle_hint_front'); } },
  { key:'image_left',  get label(){ return t('btn_capture_left');  }, get hint(){ return t('angle_hint_left');  } },
  { key:'image_right', get label(){ return t('btn_save_student');  }, get hint(){ return t('angle_hint_right'); } },
];

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
  const angle = REG_ANGLES[regStepIndex];
  if (hint  && angle) hint.textContent  = angle.hint;
  if (label && angle) label.textContent = angle.label;
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
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error('getUserMedia not available');
    }
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
    if (tab === 'dashboard') loadDashboard();
    if (tab === 'hardware') loadServoSettings();
  });
});

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
  if (dashPhotoTitle) dashPhotoTitle.textContent = t('dash_photo_title');
  if (dashPhotoMeta) dashPhotoMeta.textContent = `${name} · ${grado}${grupo} · ${turno}`;
  if (dashPhotoFallback) dashPhotoFallback.classList.add('hidden');
  dashPhotoImg.src = `/api/credencial/${student.id}?t=${Date.now()}`;
  dashPhotoImg.onerror = () => {
    if (dashPhotoFallback) dashPhotoFallback.classList.remove('hidden');
  };
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

// ════ ADMIN: ESTUDIANTES ════
async function loadStudents() {
  const tbody = document.querySelector('#studentsTable tbody');
  const msg   = document.getElementById('admStudentsMsg');
  if (!tbody) return;
  try {
    const res  = await fetch('/api/admin/students');
    const data = await res.json();
    const list = data.students || data || [];
    tbody.innerHTML = list.map(s => `
      <tr>
        <td>${s.id}</td><td>${s.nombre}</td><td>${s.grado}</td>
        <td>${s.letra||s.grupo||'---'}</td><td>${s.turno}</td>
        <td style="text-align:center">${s.estado_activo !== 0 ? '&#10003;':'&#10007;'}</td>
        <td><button style="padding:4px 9px;font-size:.72rem;box-shadow:none;background:#B91C1C"
          onclick="deleteStudent(${s.id})">Eliminar</button></td>
      </tr>`).join('');
    if (msg) { msg.textContent = `${list.length} estudiantes.`; msg.className = 'feedback waiting'; }
  } catch (_) { if (msg) { msg.textContent = 'Error al cargar.'; msg.className = 'feedback denied'; } }
}

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
    if (cfg.scale != null)     document.getElementById('cfgScale').value     = cfg.scale;
    if (cfg.tolerance != null) document.getElementById('cfgTolerance').value = cfg.tolerance;
    if (cfg.cooldown_seconds != null)  document.getElementById('cfgCooldown').value  = cfg.cooldown_seconds;
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
        scale:     parseFloat(document.getElementById('cfgScale')?.value),
        tolerance: parseFloat(document.getElementById('cfgTolerance')?.value),
        cooldown_seconds:  parseFloat(document.getElementById('cfgCooldown')?.value),
      }),
    });
    const data = await res.json();
    if (msg) { msg.textContent = data.message||(data.ok?'Guardado.':'Error'); msg.className='feedback '+(data.ok?'granted':'denied'); }
    if (data.ok) updateModelTestValues();
  } catch (_) {}
});

// ════ ADMIN: PRUEBA MODELO ════
let modelTestStream = null;
const modelTestModal = document.getElementById('modelTestModal');
const modelTestOverlay = document.getElementById('modelTestOverlay');
const modelTestClose = document.getElementById('modelTestClose');
const modelTestVideo = document.getElementById('modelTestVideo');
const modelTestCanvas = document.getElementById('modelTestCanvas');
const modelTestFps = document.getElementById('modelTestFps');
const modelTestFaces = document.getElementById('modelTestFaces');
const modelTestScale = document.getElementById('modelTestScale');
const modelTestTolerance = document.getElementById('modelTestTolerance');
const modelTestCooldown = document.getElementById('modelTestCooldown');
let modelTestDetector = null;
let modelTestAnimId = null;
let modelTestFrames = 0;
let modelTestLastTick = 0;

function updateModelTestValues() {
  const scale = document.getElementById('cfgScale')?.value;
  const tolerance = document.getElementById('cfgTolerance')?.value;
  const cooldown = document.getElementById('cfgCooldown')?.value;
  if (modelTestScale) modelTestScale.textContent = scale || '--';
  if (modelTestTolerance) modelTestTolerance.textContent = tolerance || '--';
  if (modelTestCooldown) modelTestCooldown.textContent = cooldown || '--';
}

async function openModelTest() {
  if (!modelTestModal) return;
  updateModelTestValues();
  modelTestModal.classList.remove('hidden');
  try {
    modelTestStream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (modelTestVideo) modelTestVideo.srcObject = modelTestStream;
    if ('FaceDetector' in window) {
      modelTestDetector = new FaceDetector({ fastMode: true, maxDetectedFaces: 3 });
    } else {
      modelTestDetector = null;
    }
    modelTestFrames = 0;
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
  if (modelTestCanvas) {
    const ctx = modelTestCanvas.getContext('2d');
    ctx?.clearRect(0, 0, modelTestCanvas.width, modelTestCanvas.height);
  }
  if (modelTestFps) modelTestFps.textContent = '--';
  if (modelTestFaces) modelTestFaces.textContent = '--';
}

async function startModelTestLoop() {
  if (!modelTestVideo || !modelTestCanvas) return;
  const ctx = modelTestCanvas.getContext('2d');
  const loop = async () => {
    if (!modelTestModal || modelTestModal.classList.contains('hidden')) return;
    if (modelTestVideo.readyState < 2) {
      modelTestAnimId = requestAnimationFrame(loop);
      return;
    }

    modelTestCanvas.width = modelTestVideo.videoWidth;
    modelTestCanvas.height = modelTestVideo.videoHeight;
    ctx?.clearRect(0, 0, modelTestCanvas.width, modelTestCanvas.height);

    let facesCount = 0;
    if (modelTestDetector && ctx) {
      try {
        const faces = await modelTestDetector.detect(modelTestVideo);
        facesCount = faces.length;
        ctx.lineWidth = 3;
        ctx.strokeStyle = 'rgba(0, 255, 140, 0.9)';
        ctx.fillStyle = 'rgba(0, 255, 140, 0.12)';
        faces.forEach(face => {
          const box = face.boundingBox;
          ctx.strokeRect(box.x, box.y, box.width, box.height);
          ctx.fillRect(box.x, box.y, box.width, box.height);
        });
      } catch (_) {
        facesCount = 0;
      }
    }

    modelTestFrames += 1;
    const now = performance.now();
    const elapsed = now - modelTestLastTick;
    if (elapsed >= 500) {
      const fps = Math.round((modelTestFrames / elapsed) * 1000);
      if (modelTestFps) modelTestFps.textContent = String(fps);
      if (modelTestFaces) modelTestFaces.textContent = String(facesCount);
      modelTestFrames = 0;
      modelTestLastTick = now;
    }

    modelTestAnimId = requestAnimationFrame(loop);
  };
  modelTestAnimId = requestAnimationFrame(loop);
}

document.getElementById('cfgTest')?.addEventListener('click', openModelTest);
modelTestOverlay?.addEventListener('click', closeModelTest);
modelTestClose?.addEventListener('click', closeModelTest);

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