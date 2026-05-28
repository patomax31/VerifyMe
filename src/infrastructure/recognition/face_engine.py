import cv2
import face_recognition

if not hasattr(face_recognition, "face_locations"):
    origin = getattr(face_recognition, "__file__", None) or getattr(face_recognition, "__path__", None)
    raise RuntimeError(
        "Invalid face_recognition module. Expected the face_recognition package with face_locations. "
        f"Loaded from: {origin}"
    )


def detect_face_encodings_from_frame(frame, scale=0.25):
    """Return face locations and encodings from a BGR frame."""
    small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb_small)
    encodings = face_recognition.face_encodings(rgb_small, boxes)
    return boxes, encodings


def _registration_scales(base_scale: float):
    """Prueba primero escalas altas (cara más grande en píxeles): los perfiles se detectan mejor."""
    base = max(0.12, min(1.0, float(base_scale)))
    raw = [1.0, 0.85, 0.7, 0.55, max(0.35, base * 2.0), base]
    seen = set()
    out = []
    for x in raw:
        k = round(x, 4)
        if k not in seen and k >= 0.12:
            seen.add(k)
            out.append(k)
    return out


def detect_face_encodings_from_frame_robust(frame, base_scale: float = 0.25):
    """
    Igual que detect_face_encodings_from_frame pero reintenta con varias escalas y
    upsample en HOG. Pensado para registro (frente y perfiles): los perfiles suelen
    no aparecer si solo se analiza el frame muy pequeño.
    """
    if frame is None or frame.size == 0:
        return [], []

    for scale in _registration_scales(base_scale):
        if scale >= 0.999:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(
            rgb,
            number_of_times_to_upsample=1,
            model="hog",
        )
        encodings = face_recognition.face_encodings(rgb, boxes, num_jitters=1)
        if len(encodings) >= 1:
            return boxes, encodings

    return [], []


def _login_match_scales(base_scale: float):
    """Menos escalas que en registro para mantener fluidez; prioriza calidad del encoding."""
    b = max(0.15, min(1.0, float(base_scale)))
    raw = [1.0, 0.82, 0.66, max(0.42, b * 1.8), b]
    seen = set()
    out = []
    for x in raw:
        k = round(x, 4)
        if k not in seen and k >= 0.15:
            seen.add(k)
            out.append(k)
    return out


def extract_login_face_encoding(frame, base_scale: float = 0.25):
    """
    Un único encoding para comparar en login: reintenta escalas hasta hallar exactamente 1 rostro.
    Alinea mejor con encodings guardados en registro robusto (frente + perfiles).
    """
    if frame is None or frame.size == 0:
        return None

    for scale in _login_match_scales(base_scale):
        if scale >= 0.999:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(
            rgb,
            number_of_times_to_upsample=1,
            model="hog",
        )
        encodings = face_recognition.face_encodings(rgb, boxes, num_jitters=1)
        if len(encodings) == 1:
            return encodings[0]
    return None


def encode_single_face_from_frame(frame):
    """Return encoding when exactly one face is present, otherwise None."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb_frame)
    if len(boxes) != 1:
        return None
    return face_recognition.face_encodings(rgb_frame, boxes)[0]


def find_first_match(known_encodings, candidate_encoding, tolerance=0.5):
    """Return index of first match, or -1 when no match exists."""
    matches = face_recognition.compare_faces(known_encodings, candidate_encoding, tolerance=tolerance)
    if True in matches:
        return matches.index(True)
    return -1
