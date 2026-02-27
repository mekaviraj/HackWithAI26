import pandas as pd
import numpy as np
from typing import Dict, List


class PerformanceAnalyzer:
    """Analyzes mock test attempts and computes strength metrics"""

    REQUIRED_COLUMNS = {
        "question": ["question", "question_text", "q", "question_id"],
        "correct": ["correct", "is_correct", "answered_correctly"],
        "time_seconds": ["time_seconds", "time", "time_taken", "seconds"],
        "topic": ["topic", "subject"],
        "subtopic": ["subtopic", "sub_topic", "chapter"],
        "difficulty": ["difficulty", "level", "diff", "difficulty_level"],
        "topic_weightage": ["topic_weightage", "weightage", "topic_priority"],
    }

    TEST_ID_COLUMNS = ["test_id", "test", "quiz_id", "attempt_id"]

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.analysis_results = {}
        self.column_map = {}
    # ...existing code...

    def analyze_performance(self):
        topic_stats = {}

        # Convert dataframe rows to dict records
        data = self.df.to_dict(orient="records")

        for row in data:
            topic = row.get('topic')
            weightage = row.get('topic_weightage')
            difficulty = row.get('difficulty_level')
            is_correct = int(row.get('is_correct', 0))

            topic_stats.setdefault(topic, {
                'mistakes': 0,
                'total': 0,
                'weightage': weightage,
                'difficulty': difficulty
            })

            topic_stats[topic]['total'] += 1

            if not is_correct:
                topic_stats[topic]['mistakes'] += 1

        # Prioritize: high weightage, hard, more mistakes
        prioritized = sorted(
            topic_stats.items(),
            key=lambda x: (
                x[1]['weightage'] == 'high',
                x[1]['difficulty'] == 'hard',
                x[1]['mistakes']
            ),
            reverse=True
        )

        return prioritized

    # ...existing code...
    def analyze(self) -> Dict:
        """Main analysis method"""
        self._normalize_columns()
        self._validate_and_clean_data()

        overall_accuracy = float(self.df["correct"].mean())
        accuracy_by_difficulty = self._accuracy_by_difficulty()
        time_comparison = self._time_comparison()
        strength_score = self._strength_score(overall_accuracy, accuracy_by_difficulty)
        strength_level = self._strength_level(strength_score)
        subtopic_ranking = self._rank_subtopics()
        strength_progression = self._strength_progression()

        self.analysis_results = {
            "summary": {
                "total_attempts": int(len(self.df)),
                "overall_accuracy": round(overall_accuracy * 100, 2),
                "avg_time_correct": round(time_comparison["avg_time_correct"], 2),
                "avg_time_incorrect": round(time_comparison["avg_time_incorrect"], 2),
                "strength_level": strength_level,
            },
            "accuracy_by_difficulty": accuracy_by_difficulty,
            "time_comparison": time_comparison,
            "strength_progression": strength_progression,
            "subtopic_ranking": subtopic_ranking,
            "topics": sorted(self.df["topic"].dropna().unique().tolist()),
            "prioritized_topics": self._prioritize_topics(),
        }

        return self.analysis_results

    def _normalize_columns(self) -> None:
        lower_map = {col.lower().strip(): col for col in self.df.columns}
        for canonical, options in self.REQUIRED_COLUMNS.items():
            for option in options:
                if option in lower_map:
                    self.column_map[canonical] = lower_map[option]
                    break

        missing = [
            key for key in self.REQUIRED_COLUMNS
            if key not in self.column_map and key != "topic_weightage"
        ]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        rename_map = {
            self.column_map["question"]: "question",
            self.column_map["correct"]: "correct",
            self.column_map["time_seconds"]: "time_seconds",
            self.column_map["topic"]: "topic",
            self.column_map["subtopic"]: "subtopic",
            self.column_map["difficulty"]: "difficulty",
        }
        if "topic_weightage" in self.column_map:
            rename_map[self.column_map["topic_weightage"]] = "topic_weightage"

        self.df.rename(columns=rename_map, inplace=True)

    def _validate_and_clean_data(self) -> None:
        self.df["correct"] = self.df["correct"].apply(self._to_bool)
        self.df["time_seconds"] = pd.to_numeric(self.df["time_seconds"], errors="coerce")
        self.df["difficulty"] = self.df["difficulty"].apply(self._normalize_difficulty)
        self.df["difficulty"] = pd.to_numeric(self.df["difficulty"], errors="coerce")

        if "topic_weightage" not in self.df.columns:
            self.df["topic_weightage"] = "low"
        self.df["topic_weightage"] = (
            self.df["topic_weightage"]
            .fillna("low")
            .astype(str)
            .str.strip()
            .str.lower()
        )
        self.df.loc[~self.df["topic_weightage"].isin(["high", "low"]), "topic_weightage"] = "low"

        self.df = self.df.dropna(subset=["correct", "time_seconds", "difficulty", "topic", "subtopic"])
        self.df = self.df[self.df["time_seconds"] >= 0]
        self.df = self.df[self.df["difficulty"].isin([1, 2, 3])]

        if self.df.empty:
            raise ValueError("No valid attempts after cleaning. Check your CSV values.")

    def _to_bool(self, value) -> bool:
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        return text in {"1", "true", "yes", "y", "correct"}

    def _normalize_difficulty(self, value):
        if pd.isna(value):
            return None
        text = str(value).strip().lower()
        mapping = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
        }
        if text in mapping:
            return mapping[text]
        return value

    def _accuracy_by_difficulty(self) -> List[Dict]:
        results = []
        for diff in [1, 2, 3]:
            subset = self.df[self.df["difficulty"] == diff]
            accuracy = float(subset["correct"].mean()) if not subset.empty else 0.0
            results.append({
                "difficulty": diff,
                "accuracy": round(accuracy * 100, 2),
                "attempts": int(len(subset)),
            })
        return results

    def _time_comparison(self) -> Dict:
        correct_times = self.df[self.df["correct"] == True]["time_seconds"]
        incorrect_times = self.df[self.df["correct"] == False]["time_seconds"]

        avg_correct = float(correct_times.mean()) if not correct_times.empty else 0.0
        avg_incorrect = float(incorrect_times.mean()) if not incorrect_times.empty else 0.0

        return {
            "avg_time_correct": avg_correct,
            "avg_time_incorrect": avg_incorrect,
        }

    def _strength_score(self, overall_accuracy: float, accuracy_by_difficulty: List[Dict]) -> float:
        hard_accuracy = next((item["accuracy"] for item in accuracy_by_difficulty if item["difficulty"] == 3), 0.0) / 100
        avg_time = float(self.df["time_seconds"].mean())

        # Speed score scaled so 120 seconds -> 0, 0 seconds -> 1
        speed_score = max(0.0, min(1.0, 1 - (avg_time / 120)))

        weighted = (0.6 * overall_accuracy) + (0.25 * hard_accuracy) + (0.15 * speed_score)
        return weighted * 100

    def _strength_level(self, strength_score: float) -> str:
        if strength_score < 40:
            return "Weak"
        if strength_score < 60:
            return "Developing"
        if strength_score < 80:
            return "Good"
        return "Strong"

    def _rank_subtopics(self) -> List[Dict]:
        grouped = self.df.groupby("subtopic")
        ranking = []
        for subtopic, data in grouped:
            accuracy = float(data["correct"].mean())
            mistakes = int((~data["correct"]).sum())
            avg_time = float(data["time_seconds"].mean()) if not data.empty else 0.0
            incorrect_subset = data[data["correct"] == False]
            avg_time_incorrect = float(incorrect_subset["time_seconds"].mean()) if not incorrect_subset.empty else 0.0
            avg_difficulty = float(data["difficulty"].mean()) if not data.empty else 0.0
            has_high_weightage = bool((data["topic_weightage"] == "high").any())
            difficulty_band = "hard" if avg_difficulty >= 2.5 else "medium" if avg_difficulty >= 1.5 else "easy"

            priority_score = (
                (100 - (accuracy * 100))
                + (mistakes * 12)
                + (10 if has_high_weightage else 0)
                + (8 if difficulty_band == "hard" else 0)
                + min(avg_time_incorrect / 20, 10)
            )

            ranking.append({
                "subtopic": subtopic,
                "topic": data["topic"].iloc[0],
                "accuracy": round(accuracy * 100, 2),
                "attempts": int(len(data)),
                "mistakes": mistakes,
                "avg_time": round(avg_time, 2),
                "avg_time_incorrect": round(avg_time_incorrect, 2),
                "difficulty": difficulty_band,
                "topic_weightage": "high" if has_high_weightage else "low",
                "priority_score": round(priority_score, 2),
            })

        ranking.sort(
            key=lambda item: (
                item["topic_weightage"] == "high",
                item["difficulty"] == "hard",
                item["mistakes"],
                item["avg_time_incorrect"],
                -item["accuracy"],
            ),
            reverse=True,
        )
        return ranking

    def _strength_progression(self) -> List[Dict]:
        test_id_col = None
        for col in self.TEST_ID_COLUMNS:
            if col in self.df.columns:
                test_id_col = col
                break

        if not test_id_col:
            return [{"test_id": "Test 1", "strength_score": round(self._strength_score(
                float(self.df["correct"].mean()),
                self._accuracy_by_difficulty()
            ), 2)}]

        progression = []
        for test_id, data in self.df.groupby(test_id_col):
            analyzer = PerformanceAnalyzer(data)
            analyzer._normalize_columns()
            analyzer._validate_and_clean_data()
            accuracy = float(analyzer.df["correct"].mean())
            strength_score = analyzer._strength_score(accuracy, analyzer._accuracy_by_difficulty())
            progression.append({
                "test_id": str(test_id),
                "strength_score": round(strength_score, 2),
            })

        return progression

    def _prioritize_topics(self) -> List[Dict]:
        grouped = self.df.groupby("topic")
        prioritized = []

        for topic, data in grouped:
            mistakes = int((~data["correct"]).sum())
            avg_difficulty = float(data["difficulty"].mean()) if not data.empty else 0.0
            has_high_weightage = bool((data["topic_weightage"] == "high").any())

            prioritized.append({
                "topic": topic,
                "mistakes": mistakes,
                "total": int(len(data)),
                "weightage": "high" if has_high_weightage else "low",
                "difficulty": "hard" if avg_difficulty >= 2.5 else "easy",
            })

        prioritized.sort(
            key=lambda item: (
                item["weightage"] == "high",
                item["difficulty"] == "hard",
                item["mistakes"],
            ),
            reverse=True,
        )
        return prioritized
