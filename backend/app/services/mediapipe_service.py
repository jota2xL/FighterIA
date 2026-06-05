"""
Module: services.mediapipe_service
Description: PoseAnalyzer — processes a martial arts video with MediaPipe Pose,
             calculates joint angles at the key frame and generates an overlay video
             with color-coded annotations (green = correct, red = incorrect).
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# ── Colors (BGR) ───────────────────────────────────────────────────────────
COLOR_CORRECT = (0, 220, 0)       # green
COLOR_INCORRECT = (0, 0, 230)     # red
COLOR_TEXT = (255, 255, 255)      # white
COLOR_REF = (0, 165, 255)         # orange — reference range label
COLOR_SKELETON = (180, 180, 180)  # light grey for skeleton lines

# ── Joint → (A_landmark, B_landmark, C_landmark) ──────────────────────────
# Angle is measured at B, formed by segments A-B and C-B
_LM = mp_pose.PoseLandmark

JOINT_LANDMARKS: dict[str, tuple] = {
    "left_elbow":            (_LM.LEFT_SHOULDER,  _LM.LEFT_ELBOW,   _LM.LEFT_WRIST),
    "right_elbow":           (_LM.RIGHT_SHOULDER, _LM.RIGHT_ELBOW,  _LM.RIGHT_WRIST),
    "left_shoulder":         (_LM.LEFT_ELBOW,     _LM.LEFT_SHOULDER,  _LM.LEFT_HIP),
    "right_shoulder":        (_LM.RIGHT_ELBOW,    _LM.RIGHT_SHOULDER, _LM.RIGHT_HIP),
    "left_knee":             (_LM.LEFT_HIP,       _LM.LEFT_KNEE,    _LM.LEFT_ANKLE),
    "right_knee":            (_LM.RIGHT_HIP,      _LM.RIGHT_KNEE,   _LM.RIGHT_ANKLE),
    "left_hip":              (_LM.LEFT_SHOULDER,  _LM.LEFT_HIP,     _LM.LEFT_KNEE),
    "right_hip":             (_LM.RIGHT_SHOULDER, _LM.RIGHT_HIP,    _LM.RIGHT_KNEE),
    "kicking_hip":           (_LM.LEFT_SHOULDER,  _LM.LEFT_HIP,     _LM.LEFT_KNEE),
    "kicking_knee":          (_LM.LEFT_HIP,       _LM.LEFT_KNEE,    _LM.LEFT_ANKLE),
    "support_knee":          (_LM.RIGHT_HIP,      _LM.RIGHT_KNEE,   _LM.RIGHT_ANKLE),
    "hip_rotation_proxy":    (_LM.LEFT_SHOULDER,  _LM.LEFT_HIP,     _LM.RIGHT_HIP),
    "hip_flexion":           (_LM.LEFT_SHOULDER,  _LM.LEFT_HIP,     _LM.LEFT_KNEE),
    "hip_extension":         (_LM.LEFT_SHOULDER,  _LM.LEFT_HIP,     _LM.LEFT_KNEE),
    "target_arm_extension":  (_LM.RIGHT_SHOULDER, _LM.RIGHT_ELBOW,  _LM.RIGHT_WRIST),
    "target_arm_lock":       (_LM.RIGHT_SHOULDER, _LM.RIGHT_ELBOW,  _LM.RIGHT_WRIST),
    "knee_pinch":            (_LM.LEFT_HIP,       _LM.LEFT_KNEE,    _LM.RIGHT_KNEE),
    "knee_bend":             (_LM.LEFT_HIP,       _LM.LEFT_KNEE,    _LM.LEFT_ANKLE),
    "knee_flexion":          (_LM.RIGHT_HIP,      _LM.RIGHT_KNEE,   _LM.RIGHT_ANKLE),
    "front_knee":            (_LM.LEFT_HIP,       _LM.LEFT_KNEE,    _LM.LEFT_ANKLE),
    "rear_knee":             (_LM.RIGHT_HIP,      _LM.RIGHT_KNEE,   _LM.RIGHT_ANKLE),
    "ankle_behind_knee":     (_LM.LEFT_HIP,       _LM.LEFT_KNEE,    _LM.RIGHT_KNEE),
}


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """
    Return the angle in degrees at vertex B formed by rays B→A and B→C.
    Uses the dot-product formula; result is in [0, 180].
    """
    ba = a - b
    bc = c - b
    norm = np.linalg.norm(ba) * np.linalg.norm(bc)
    if norm < 1e-8:
        return 0.0
    cosine = np.clip(np.dot(ba, bc) / norm, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


@dataclass
class VideoAnalysisResult:
    joint_angles: dict[str, float] = field(default_factory=dict)
    frame_count: int = 0
    key_frame_index: int = 0
    pose_detected: bool = False
    speed_proxy: float = 0.0    # average wrist velocity between consecutive frames


class PoseAnalyzer:
    """
    Processes a martial arts video with MediaPipe Pose.
    Call analyze_video() once per video; call close() when done.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self.pose = mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=1,
        )

    # ── Public API ────────────────────────────────────────────────────────

    def analyze_video(
        self,
        input_path: pathlib.Path,
        output_path: pathlib.Path,
        biomechanical_refs: dict[str, dict],
    ) -> VideoAnalysisResult:
        """
        Process every frame, measure joint angles at the key frame,
        and write an annotated overlay video to output_path.

        Args:
            input_path: path to the original video file
            output_path: path where the overlay MP4 will be saved
            biomechanical_refs: {joint_name: {min_angle, max_angle, optimal_angle, weight}}

        Returns:
            VideoAnalysisResult with joint_angles populated (or pose_detected=False)
        """
        result = VideoAnalysisResult()

        # ── First pass: collect all per-frame landmarks ───────────────────
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        all_landmarks: list[list | None] = []  # one entry per frame

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            pose_result = self.pose.process(rgb)
            if pose_result.pose_landmarks:
                all_landmarks.append(pose_result.pose_landmarks.landmark)
                result.pose_detected = True
            else:
                all_landmarks.append(None)

        cap.release()
        result.frame_count = len(all_landmarks)

        if not result.pose_detected:
            return result

        # ── Key frame detection ──────────────────────────────────────────
        result.key_frame_index = self._find_key_frame(all_landmarks)
        key_lm = all_landmarks[result.key_frame_index]

        # ── Calculate angles at key frame ────────────────────────────────
        if key_lm is not None:
            for joint_name, triplet in JOINT_LANDMARKS.items():
                try:
                    a = np.array([key_lm[triplet[0].value].x, key_lm[triplet[0].value].y])
                    b = np.array([key_lm[triplet[1].value].x, key_lm[triplet[1].value].y])
                    c = np.array([key_lm[triplet[2].value].x, key_lm[triplet[2].value].y])
                    result.joint_angles[joint_name] = calculate_angle(a, b, c)
                except (IndexError, AttributeError):
                    pass

        # ── Speed proxy ───────────────────────────────────────────────────
        result.speed_proxy = self._calculate_speed_proxy(all_landmarks)

        # ── Second pass: write overlay video ─────────────────────────────
        cap2 = cv2.VideoCapture(str(input_path))
        # avc1 = H.264: required for browser playback; bundled in opencv-python-headless via FFMPEG
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        if not writer.isOpened():
            cap2.release()
            raise RuntimeError(
                "OpenCV VideoWriter could not be opened. "
                "Check that opencv-python-headless is correctly installed."
            )

        frame_idx = 0
        while True:
            ok, frame = cap2.read()
            if not ok:
                break

            lm = all_landmarks[frame_idx] if frame_idx < len(all_landmarks) else None

            if lm is not None:
                self._draw_skeleton(frame, lm, width, height)
                if frame_idx == result.key_frame_index:
                    self._draw_angle_annotations(
                        frame, lm, biomechanical_refs, result.joint_angles, width, height
                    )

            writer.write(frame)
            frame_idx += 1

        cap2.release()
        writer.release()

        return result

    def close(self) -> None:
        """Release MediaPipe resources. Call when the analyzer is no longer needed."""
        self.pose.close()

    # ── Private helpers ───────────────────────────────────────────────────

    def _find_key_frame(self, all_landmarks: list) -> int:
        """
        Identify the frame where the right elbow is most extended.
        This serves as a proxy for the peak-execution moment across all disciplines.
        """
        max_angle = -1.0
        key_idx = 0

        for idx, lm in enumerate(all_landmarks):
            if lm is None:
                continue
            try:
                a = np.array([lm[_LM.RIGHT_SHOULDER.value].x, lm[_LM.RIGHT_SHOULDER.value].y])
                b = np.array([lm[_LM.RIGHT_ELBOW.value].x,    lm[_LM.RIGHT_ELBOW.value].y])
                c = np.array([lm[_LM.RIGHT_WRIST.value].x,    lm[_LM.RIGHT_WRIST.value].y])
                angle = calculate_angle(a, b, c)
                if angle > max_angle:
                    max_angle = angle
                    key_idx = idx
            except (IndexError, AttributeError):
                pass

        return key_idx

    def _calculate_speed_proxy(self, all_landmarks: list) -> float:
        """
        Estimate technique speed as the mean wrist displacement between consecutive frames.
        Higher value → faster movement.
        """
        velocities: list[float] = []
        prev: np.ndarray | None = None

        for lm in all_landmarks:
            if lm is None:
                prev = None
                continue
            try:
                wrist = lm[_LM.RIGHT_WRIST.value]
                pos = np.array([wrist.x, wrist.y])
                if prev is not None:
                    velocities.append(float(np.linalg.norm(pos - prev)))
                prev = pos
            except (IndexError, AttributeError):
                prev = None

        return float(np.mean(velocities)) if velocities else 0.0

    def _draw_skeleton(
        self, frame: np.ndarray, landmarks: list, width: int, height: int
    ) -> None:
        """Draw MediaPipe pose skeleton on the frame in-place."""
        # Build a NormalizedLandmarkList proto for the drawing utility
        landmark_list = landmark_pb2.NormalizedLandmarkList()
        for lm in landmarks:
            new_lm = landmark_list.landmark.add()
            new_lm.x = lm.x
            new_lm.y = lm.y
            new_lm.z = lm.z

        mp_drawing.draw_landmarks(
            frame,
            landmark_list,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=COLOR_SKELETON, thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=COLOR_SKELETON, thickness=2),
        )

    def _draw_angle_annotations(
        self,
        frame: np.ndarray,
        landmarks: list,
        biomechanical_refs: dict[str, dict],
        joint_angles: dict[str, float],
        width: int,
        height: int,
    ) -> None:
        """
        Overlay angle values at each measured joint on the key frame.
        Green circle = within correct range, red circle = outside range.
        """
        for joint_name, ref in biomechanical_refs.items():
            if joint_name not in JOINT_LANDMARKS:
                continue
            if joint_name not in joint_angles:
                continue

            triplet = JOINT_LANDMARKS[joint_name]
            try:
                b_lm = landmarks[triplet[1].value]
                cx = int(b_lm.x * width)
                cy = int(b_lm.y * height)

                angle = joint_angles[joint_name]
                is_correct = ref["min_angle"] <= angle <= ref["max_angle"]
                dot_color = COLOR_CORRECT if is_correct else COLOR_INCORRECT

                # Filled circle at joint
                cv2.circle(frame, (cx, cy), 12, dot_color, -1)
                cv2.circle(frame, (cx, cy), 12, (0, 0, 0), 1)  # thin black border

                # Measured angle
                cv2.putText(
                    frame,
                    f"{angle:.0f}\xb0",
                    (cx + 16, cy),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.52,
                    COLOR_TEXT,
                    1,
                    cv2.LINE_AA,
                )
                # Reference range
                cv2.putText(
                    frame,
                    f"[{ref['min_angle']:.0f}-{ref['max_angle']:.0f}]",
                    (cx + 16, cy + 16),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.36,
                    COLOR_REF,
                    1,
                    cv2.LINE_AA,
                )
            except (IndexError, AttributeError, KeyError):
                pass
