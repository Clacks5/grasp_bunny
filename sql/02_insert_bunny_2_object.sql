USE grasp_bunny;

INSERT INTO object(name, mesh_path)
VALUES('bunny', 'one/bunny.stl')
ON DUPLICATE KEY UPDATE
    mesh_path = VALUES(mesh_path);

SELECT * FROM object;
