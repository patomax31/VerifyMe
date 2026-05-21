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
    btn_create_student:'Crear', btn_refresh:'Refrescar',
    students_mgmt:'Gestión de estudiantes.',
    no_camera:'No se pudo acceder a la cámara.',
    clock_status:'SISTEMA EN LÍNEA · CÁMARA ACTIVA',
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
    btn_create_student:'Create', btn_refresh:'Refresh',
    students_mgmt:'Student management.',
    no_camera:'Could not access camera.',
    clock_status:'SYSTEM ONLINE · CAMERA ACTIVE',
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

// ════ ACCESO FACIAL ════
let loginStream      = null;
let loginInterval    = null;
let loginLivId       = null;
let loginLivOk       = false;
let loginDeniedCount = 0;

const loginVideo      = document.getElementById('loginVideo');
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

function stopLoginCamera() {
  clearInterval(loginInterval); loginInterval = null;
  if (loginStream) loginStream.getTracks().forEach(t => t.stop());
  loginStream = null;
  if (loginVideo)  loginVideo.srcObject  = null;
  if (loginStart)  loginStart.disabled   = false;
  if (loginStop)   loginStop.disabled    = true;
  if (camOverlay)  camOverlay.classList.remove('hidden');
  loginLivId = null; loginLivOk = false;
}

function showAccessStep(n) {
  const s1 = document.getElementById('access-step1');
  const s2 = document.getElementById('access-step2');
  if (n === 1) { s1?.classList.remove('hidden'); s2?.classList.add('hidden'); }
  else         { s1?.classList.add('hidden');    s2?.classList.remove('hidden'); }
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
  if (!loginVideo || !loginCanvas || !loginLivId) return;
  loginCanvas.width  = loginVideo.videoWidth;
  loginCanvas.height = loginVideo.videoHeight;
  loginCanvas.getContext('2d').drawImage(loginVideo, 0, 0);
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
  if (!loginVideo || !loginCanvas) return;
  loginCanvas.width  = loginVideo.videoWidth;
  loginCanvas.height = loginVideo.videoHeight;
  loginCanvas.getContext('2d').drawImage(loginVideo, 0, 0);
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
const regCanvas  = document.getElementById('regCanvas');
const regStart   = document.getElementById('regStart');
const regCapture = document.getElementById('regCapture');
const regStop    = document.getElementById('regStop');
const regMsg     = document.getElementById('regMessage');
const regCamOv   = document.getElementById('regCameraOverlay');

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
  if (regStream) regStream.getTracks().forEach(t => t.stop());
  regStream = null;
  if (regVideo)   regVideo.srcObject  = null;
  if (regStart)   regStart.disabled   = false;
  if (regCapture) regCapture.disabled = true;
  if (regStop)    regStop.disabled    = true;
  if (regCamOv)   regCamOv.classList.remove('hidden');
}

document.getElementById('regGoToCamera')?.addEventListener('click', () => {
  const nombre = document.getElementById('regNombre')?.value.trim();
  const grado  = document.getElementById('regGrado')?.value;
  const letra  = document.getElementById('regLetra')?.value.trim().toUpperCase();
  const turno  = document.getElementById('regTurno')?.value;
  const msg1   = document.getElementById('regStep1Msg');

  if (!nombre) { if (msg1) { msg1.textContent = 'Ingresa el nombre.'; msg1.className='feedback denied'; } return; }
  if (!letra)  { if (msg1) { msg1.textContent = 'Ingresa el grupo.';  msg1.className='feedback denied'; } return; }

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
    regStream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (regVideo)   regVideo.srcObject  = regStream;
    if (regCamOv)   regCamOv.classList.add('hidden');
    if (regStart)   regStart.disabled   = true;
    if (regCapture) regCapture.disabled = false;
    if (regStop)    regStop.disabled    = false;
    if (regMsg)     { regMsg.textContent = t('reg_cam_ready'); regMsg.className = 'feedback waiting'; }
  } catch (_) {
    if (regMsg) { regMsg.textContent = t('no_camera'); regMsg.className = 'feedback denied'; }
  }
});

regCapture?.addEventListener('click', async () => {
  if (!regVideo || !regCanvas) return;
  regCanvas.width  = regVideo.videoWidth;
  regCanvas.height = regVideo.videoHeight;
  regCanvas.getContext('2d').drawImage(regVideo, 0, 0);
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
  });
});

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
        <td style="text-align:center">${s.activo !== false ? '&#10003;':'&#10007;'}</td>
        <td><button style="padding:4px 9px;font-size:.72rem;box-shadow:none;background:#B91C1C"
          onclick="deleteStudent(${s.id})">Eliminar</button></td>
      </tr>`).join('');
    if (msg) { msg.textContent = `${list.length} estudiantes.`; msg.className = 'feedback waiting'; }
  } catch (_) { if (msg) { msg.textContent = 'Error al cargar.'; msg.className = 'feedback denied'; } }
}

window.deleteStudent = async id => {
  if (!confirm(`¿Eliminar estudiante #${id}?`)) return;
  try { await fetch(`/api/admin/students/${id}`, { method:'DELETE' }); loadStudents(); } catch (_) {}
};

document.getElementById('admRefresh')?.addEventListener('click', loadStudents);

document.getElementById('admCreate')?.addEventListener('click', async () => {
  const msg    = document.getElementById('admStudentsMsg');
  const nombre = document.getElementById('admNombre')?.value.trim();
  const grado  = document.getElementById('admGrado')?.value;
  const letra  = document.getElementById('admGrupo')?.value.trim().toUpperCase();
  const turno  = document.getElementById('admTurno')?.value;
  if (!nombre || !letra) { if (msg) { msg.textContent='Completa nombre y grupo.'; msg.className='feedback denied'; } return; }
  try {
    const res  = await fetch('/api/admin/students', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ nombre, grado, letra, turno }),
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
    const res  = await fetch('/api/admin/config');
    const data = await res.json();
    if (data.scale)     document.getElementById('cfgScale').value     = data.scale;
    if (data.tolerance) document.getElementById('cfgTolerance').value = data.tolerance;
    if (data.cooldown)  document.getElementById('cfgCooldown').value  = data.cooldown;
    if (msg) { msg.textContent='Configuración cargada.'; msg.className='feedback granted'; }
  } catch (_) {}
});

document.getElementById('cfgSave')?.addEventListener('click', async () => {
  const msg = document.getElementById('cfgMsg');
  try {
    const res  = await fetch('/api/admin/config', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        scale:     parseFloat(document.getElementById('cfgScale')?.value),
        tolerance: parseFloat(document.getElementById('cfgTolerance')?.value),
        cooldown:  parseFloat(document.getElementById('cfgCooldown')?.value),
      }),
    });
    const data = await res.json();
    if (msg) { msg.textContent = data.message||(data.ok?'Guardado.':'Error'); msg.className='feedback '+(data.ok?'granted':'denied'); }
  } catch (_) {}
});

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
        <td>${a.id}</td><td>${a.numero_empleado}</td><td>${a.nombre}</td>
        <td>${a.rol}</td><td>${a.correo||'---'}</td>
        <td style="text-align:center">${a.activo !== false ? '&#10003;':'&#10007;'}</td>
      </tr>`).join('');
    if (msg) { msg.textContent=`${list.length} administradores.`; msg.className='feedback waiting'; }
  } catch (_) {}
}

document.getElementById('adminRefresh')?.addEventListener('click', loadAdmins);

document.getElementById('adminCreate')?.addEventListener('click', async () => {
  const msg  = document.getElementById('adminMsg');
  const body = {
    numero_empleado: document.getElementById('adminNum')?.value.trim(),
    nombre:          document.getElementById('adminNombre')?.value.trim(),
    rol:             document.getElementById('adminRol')?.value.trim(),
    correo:          document.getElementById('adminCorreo')?.value.trim(),
    password:        document.getElementById('adminPass')?.value,
  };
  if (!body.numero_empleado || !body.nombre || !body.password) {
    if (msg) { msg.textContent='Completa los campos obligatorios.'; msg.className='feedback denied'; }
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