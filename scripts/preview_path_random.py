import io
import numpy as np
import mysql.connector

from one import (
    ovw, ossop, osso, ouc,
    khi_rs007l, or_2fg7,
)

from db_config import DB_CONFIG
from paths import BUNNY_MESH_PATH

def blob_to_ndarray(blob):
    return np.load(io.BytesIO(blob))

def load_random_path_candidate():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 経路計算が成功しているデータ（path_joint_values が NULL でないもの）を取得
    cur.execute(
        """
        SELECT
            pgik.placement_grasp_ik_id,
            pgik.placement_id,
            pgik.grasp_id,
            pgik.path_joint_values,
            p.world_pos,
            p.world_rotmat
        FROM placement_grasp_ik AS pgik
        JOIN placement AS p ON pgik.placement_id = p.placement_id
        WHERE pgik.path_joint_values IS NOT NULL
        ORDER BY RAND()
        LIMIT 1
        """
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return None

    (
        pgik_id,
        placement_id,
        grasp_id,
        path_blob,
        bunny_pos_blob,
        bunny_rot_blob,
    ) = row

    return {
        "pgik_id": pgik_id,
        "placement_id": placement_id,
        "grasp_id": grasp_id,
        "path_qs": blob_to_ndarray(path_blob),
        "bunny_pos": blob_to_ndarray(bunny_pos_blob),
        "bunny_rot": blob_to_ndarray(bunny_rot_blob),
    }

def main():
    base = ovw.World(
        cam_pos=(2.0, 2.0, 1.5),
        cam_lookat_pos=(0, 0, 0.5),
        toggle_auto_cam_orbit=False,
    )

    ossop.frame().attach_to(base.scene)
    ground = ossop.plane(pos=(0, 0, 0))
    ground.attach_to(base.scene)

    bunny = osso.SceneObject.from_file(
        str(BUNNY_MESH_PATH),
        collision_type=ouc.CollisionType.MESH,
    )
    bunny.attach_to(base.scene)

    robot = khi_rs007l.RS007L()
    robot.attach_to(base.scene)

    gripper = or_2fg7.OR2FG7()
    gripper.attach_to(base.scene)
    robot.engage(gripper)

    home_qs = robot.qs.copy()

    state = {
        "path": [],
        "cursor": 0,
        "waiting": False,
        "wait_time": 0.0,
    }

    def select_next():
        c = load_random_path_candidate()
        if c is None:
            print("DBに経路データが見つかりません。先に経路生成スクリプトを実行してください。")
            return

        bunny.pos = c["bunny_pos"]
        bunny.rotmat = c["bunny_rot"]

        # DBから読み込んだ経路をそのままセット
        state["path"] = c["path_qs"]
        state["cursor"] = 0
        state["waiting"] = False
        state["wait_time"] = 0.0

        robot.fk(home_qs)

        print(
            f"pgik={c['pgik_id']} "
            f"placement={c['placement_id']} "
            f"grasp={c['grasp_id']} "
            f"steps={len(state['path'])}"
        )

    select_next()

    def tick(dt):
        if not state["waiting"]:
            if state["cursor"] < len(state["path"]):
                robot.fk(qs=state["path"][state["cursor"]])
                state["cursor"] += 1
            else:
                state["waiting"] = True
                state["wait_time"] = 0.0
        else:
            state["wait_time"] += dt
            if state["wait_time"] > 1.0:
                select_next()

    base.schedule_interval(tick, interval=0.02)
    base.run()

if __name__ == "__main__":
    main()