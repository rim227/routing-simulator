import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path


class RoutingSimulatorApp(tk.Tk):
    """
    Network Routing Simulation System
    - CSV 파일 불러오기
    - 시나리오 1/2 실행
    - 최단 경로 계산 및 비교
    - 그래프 이미지 저장 / 라우팅 테이블 저장 / 시나리오 비교 CSV 저장
    """

    def __init__(self):
        super().__init__()

        self.title("Network Routing Simulation System")
        self.geometry("420x320")

        # 상태 변수
        self.csv_path: Path | None = None
        self.graph_original: nx.DiGraph | None = None
        self.graph_scenario2: nx.DiGraph | None = None
        self.source_node = "A"
        self.target_node = "L"

        self.scenario1_result = None  # (path, cost)
        self.scenario2_result = None

        self._build_start_screen()

    # ------------- UI 화면 구성 ------------- #

    def _clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _build_start_screen(self):
        """시작 화면: CSV 불러오기, 시나리오 선택, 실행 시작"""
        self._clear_screen()

        title = tk.Label(
            self,
            text="Network Routing Simulation System",
            font=("맑은 고딕", 14, "bold"),
        )
        title.pack(pady=18)

        btn_csv = tk.Button(
            self, text="CSV 파일 불러오기", width=25, command=self.load_csv_file
        )
        btn_csv.pack(pady=6)

        btn_scenario_info = tk.Button(
            self, text="시나리오 설명 보기", width=25, command=self.show_scenario_info
        )
        btn_scenario_info.pack(pady=6)

        btn_run = tk.Button(
            self, text="실행 시작", width=25, command=self.run_simulation
        )
        btn_run.pack(pady=18)

        status_text = (
            f"선택된 CSV: {self.csv_path.name}"
            if self.csv_path
            else "선택된 CSV: 없음"
        )
        self.label_status = tk.Label(self, text=status_text, fg="gray")
        self.label_status.pack(pady=4)

    # ------------- CSV 로드 & 그래프 생성 ------------- #

    def load_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="CSV 파일 선택",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            messagebox.showerror("에러", f"CSV 파일을 읽는 중 오류 발생:\n{e}")
            return

        required_cols = {"Start_Node", "End_Node", "Weight"}
        if not required_cols.issubset(df.columns):
            messagebox.showerror(
                "에러",
                "CSV 컬럼이 올바르지 않습니다.\n필수 컬럼: Start_Node, End_Node, Weight",
            )
            return

        self.csv_path = Path(file_path)

        # 원본 그래프 생성
        self.graph_original = nx.DiGraph()
        for _, row in df.iterrows():
            s, e, w = row["Start_Node"], row["End_Node"], row["Weight"]
            self.graph_original.add_edge(str(s), str(e), weight=float(w))

        # 시나리오2용 그래프는 원본 복사 후 비용만 변경
        self.graph_scenario2 = self.graph_original.copy()
        self.apply_scenario2_cost_change()

        # 상태 업데이트
        nodes = self.graph_original.number_of_nodes()
        edges = self.graph_original.number_of_edges()
        self.label_status.config(
            text=f"선택된 CSV: {self.csv_path.name} (노드 {nodes}개, 링크 {edges}개)"
        )

        messagebox.showinfo(
            "CSV 로드 완료",
            f"파일: {self.csv_path.name}\n노드: {nodes}개, 링크: {edges}개",
        )

    def apply_scenario2_cost_change(self):
        """
        시나리오2: 특정 링크 비용을 증가시켜 혼잡 구간 가정
        - C -> F : 2 -> 15
        - G -> J : 3 -> 12
        (존재하는 경우에만 수정)
        """
        if self.graph_scenario2 is None:
            return

        def safe_update(u, v, new_weight):
            if self.graph_scenario2.has_edge(u, v):
                self.graph_scenario2[u][v]["weight"] = new_weight

        safe_update("C", "F", 15.0)
        safe_update("G", "J", 12.0)

    # ------------- 시나리오 설명 ------------- #

    def show_scenario_info(self):
        info = (
            "시나리오 1: CSV에 정의된 원본 비용 그대로 사용하여\n"
            "           A → L 구간의 최단 경로를 계산합니다.\n\n"
            "시나리오 2: 특정 링크(C→F, G→J)의 비용을 크게 증가시켜\n"
            "           혼잡 구간을 가정하고, 다시 A → L 최단 경로를 계산합니다.\n"
            "           두 시나리오의 경로 및 총 비용을 비교합니다."
        )
        messagebox.showinfo("시나리오 설명", info)

    # ------------- 시뮬레이션 전체 실행 ------------- #

    def run_simulation(self):
        if self.graph_original is None:
            messagebox.showwarning("알림", "먼저 CSV 파일을 불러와 주세요.")
            return

        # 시나리오1 계산
        try:
            path1, cost1 = self.compute_shortest_path(
                self.graph_original, self.source_node, self.target_node
            )
            self.scenario1_result = (path1, cost1)
        except nx.NetworkXNoPath:
            messagebox.showerror(
                "에러",
                f"시나리오1: {self.source_node}에서 {self.target_node}까지 경로가 없습니다.",
            )
            return

        # 시나리오2 계산
        try:
            path2, cost2 = self.compute_shortest_path(
                self.graph_scenario2, self.source_node, self.target_node
            )
            self.scenario2_result = (path2, cost2)
        except nx.NetworkXNoPath:
            messagebox.showerror(
                "에러",
                f"시나리오2: {self.source_node}에서 {self.target_node}까지 경로가 없습니다.",
            )
            return

        # 각 단계별 예시 화면처럼 Toplevel로 보여주기
        self.show_result_windows()

    # ------------- 경로 계산 ------------- #

    @staticmethod
    def compute_shortest_path(G: nx.DiGraph, source: str, target: str):
        path = nx.shortest_path(G, source=source, target=target, weight="weight")
        cost = nx.shortest_path_length(G, source=source, target=target, weight="weight")
        return path, cost

    # ------------- UI: 결과창들 ------------- #

    def show_result_windows(self):
        # 1) 경로 계산 결과 화면 (시나리오1)
        path1, cost1 = self.scenario1_result
        win1 = tk.Toplevel(self)
        win1.title("경로 계산 결과 화면")
        tk.Label(
            win1, text="최단 경로 계산 결과", font=("맑은 고딕", 12, "bold")
        ).pack(pady=10)

        txt = (
            f"출발 노드: {self.source_node}\n"
            f"도착 노드: {self.target_node}\n"
            f"시나리오1 최단 경로: {' → '.join(path1)}\n"
            f"시나리오1 총 비용: {cost1:.1f}"
        )
        tk.Label(win1, text=txt, justify="left").pack(padx=15, pady=10)
        tk.Button(win1, text="확인", command=win1.destroy).pack(pady=8)

        # 2) 시나리오 비교 결과 화면
        path2, cost2 = self.scenario2_result
        win2 = tk.Toplevel(self)
        win2.title("시나리오 비교 결과 화면")
        tk.Label(
            win2, text="시나리오 비교 결과", font=("맑은 고딕", 12, "bold")
        ).pack(pady=10)

        changed = "O" if path1 != path2 or cost1 != cost2 else "X"

        txt2 = (
            f"시나리오1 경로: {' → '.join(path1)} (비용 {cost1:.1f})\n"
            f"시나리오2 경로: {' → '.join(path2)} (비용 {cost2:.1f})\n"
            f"경로 변경 발생: {changed}"
        )
        tk.Label(win2, text=txt2, justify="left").pack(padx=15, pady=10)
        tk.Button(win2, text="확인", command=win2.destroy).pack(pady=8)

        # 3) 출력 파일 저장 화면
        win3 = tk.Toplevel(self)
        win3.title("출력 파일 저장 화면")
        tk.Label(
            win3, text="출력 파일 저장", font=("맑은 고딕", 12, "bold")
        ).pack(pady=10)

        btn_rt = tk.Button(
            win3,
            text="라우팅 테이블 CSV 저장",
            width=26,
            command=self.save_routing_tables,
        )
        btn_rt.pack(pady=4)

        btn_img = tk.Button(
            win3, text="경로 이미지 저장", width=26, command=self.save_graph_images
        )
        btn_img.pack(pady=4)

        btn_cmp = tk.Button(
            win3,
            text="시나리오 비교 CSV 저장",
            width=26,
            command=self.save_scenario_comparison,
        )
        btn_cmp.pack(pady=4)

    # ------------- 파일 저장 기능들 ------------- #

    def save_routing_tables(self):
        if self.graph_original is None:
            return

        save_dir = filedialog.askdirectory(title="저장할 폴더 선택")
        if not save_dir:
            return
        save_dir = Path(save_dir)

        # 시나리오1 라우팅 테이블
        df1 = self.build_routing_table(self.graph_original, self.source_node)
        df1.to_csv(save_dir / "routing_table_scenario1.csv", index=False, encoding="utf-8-sig")

        # 시나리오2 라우팅 테이블
        df2 = self.build_routing_table(self.graph_scenario2, self.source_node)
        df2.to_csv(save_dir / "routing_table_scenario2.csv", index=False, encoding="utf-8-sig")

        messagebox.showinfo(
            "저장 완료",
            f"라우팅 테이블 CSV 2개가 저장되었습니다.\n폴더: {save_dir}",
        )

    @staticmethod
    def build_routing_table(G: nx.DiGraph, source: str) -> pd.DataFrame:
        nodes = sorted(G.nodes())
        records = []

        for dst in nodes:
            if dst == source:
                continue
            try:
                path = nx.shortest_path(G, source=source, target=dst, weight="weight")
                cost = nx.shortest_path_length(
                    G, source=source, target=dst, weight="weight"
                )
                next_hop = path[1] if len(path) > 1 else "-"
                records.append(
                    {
                        "Source": source,
                        "Destination": dst,
                        "NextHop": next_hop,
                        "TotalCost": cost,
                        "Path": " → ".join(path),
                    }
                )
            except nx.NetworkXNoPath:
                records.append(
                    {
                        "Source": source,
                        "Destination": dst,
                        "NextHop": "-",
                        "TotalCost": float("inf"),
                        "Path": "경로 없음",
                    }
                )

        return pd.DataFrame(records)

    def save_graph_images(self):
        if self.graph_original is None:
            return

        save_dir = filedialog.askdirectory(title="그래프 이미지를 저장할 폴더 선택")
        if not save_dir:
            return
        save_dir = Path(save_dir)

        # 시나리오1
        self.draw_and_save_graph(
            self.graph_original,
            self.scenario1_result[0],
            save_dir / "graph_scenario1.png",
            title="Scenario 1: Original Costs",
        )

        # 시나리오2
        self.draw_and_save_graph(
            self.graph_scenario2,
            self.scenario2_result[0],
            save_dir / "graph_scenario2.png",
            title="Scenario 2: Modified Costs",
        )

        messagebox.showinfo(
            "저장 완료", f"그래프 이미지 2개가 저장되었습니다.\n폴더: {save_dir}"
        )

    @staticmethod
    def draw_and_save_graph(G: nx.DiGraph, path, file_path: Path, title: str = ""):
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G, seed=42)

        # 전체 그래프
        nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=800)
        nx.draw_networkx_labels(G, pos, font_size=10)
        nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True, arrowsize=12)

        # 비용 라벨
        edge_labels = {
            (u, v): f"{d['weight']:.0f}" for u, v, d in G.edges(data=True)
        }
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

        # 최단 경로 강조
        if path is not None and len(path) > 1:
            path_edges = list(zip(path[:-1], path[1:]))
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=path_edges,
                edge_color="red",
                width=2.5,
                arrows=True,
                arrowsize=14,
            )

        plt.title(title)
        plt.tight_layout()
        plt.savefig(file_path, dpi=200)
        plt.close()

    def save_scenario_comparison(self):
        if not (self.scenario1_result and self.scenario2_result):
            return

        save_dir = filedialog.askdirectory(title="시나리오 비교 CSV 저장 폴더 선택")
        if not save_dir:
            return
        save_dir = Path(save_dir)

        path1, cost1 = self.scenario1_result
        path2, cost2 = self.scenario2_result

        df = pd.DataFrame(
            [
                {
                    "Scenario": "1",
                    "Path": " → ".join(path1),
                    "TotalCost": cost1,
                },
                {
                    "Scenario": "2",
                    "Path": " → ".join(path2),
                    "TotalCost": cost2,
                },
            ]
        )
        df.to_csv(save_dir / "scenario_comparison.csv", index=False, encoding="utf-8-sig")

        messagebox.showinfo(
            "저장 완료", f"시나리오 비교 결과 CSV가 저장되었습니다.\n폴더: {save_dir}"
        )


if __name__ == "__main__":
    app = RoutingSimulatorApp()
    app.mainloop()
