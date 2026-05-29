import json
from sqlalchemy import text
from sqlalchemy.orm import Session

def get_spatial_data_service(request, db: Session):
    query = """
            SELECT
                id,
                category,
                region_name,
                ST_AsGeoJSON(ST_Simplify(geom, 0.0001)),
                properties
            FROM spatial_data
            WHERE geom IS NOT NULL
        """
    params = {}
    if request.region_name:
        query += " AND region_name ILIKE :region_name"
        params["region_name"] = f"%{request.region_name}%"
    if request.category:
        query += " AND category = :category"
        params["category"] = request.category
    if all([
        request.minLng is not None,
        request.minLat is not None,
        request.maxLng is not None,
        request.maxLat is not None
    ]):
        query += """
            AND geom && ST_MakeEnvelope(:minLng, :minLat, :maxLng, :maxLat, 4326)
        """
        params.update({
            "minLng": request.minLng,
            "minLat": request.minLat,
            "maxLng": request.maxLng,
            "maxLat": request.maxLat
        })
    query += " ORDER BY id DESC"
    limit = request.limit if request.limit else 50000
    params["limit"] = limit
    query += " LIMIT :limit"
    result = db.execute(text(query), params).fetchall()
    features = []
    for row in result:
        geometry = row[3]
        if isinstance(geometry, str):
            geometry = json.loads(geometry)
        props = row[4] or {}
        if isinstance(props, str):
            props = json.loads(props)
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                **props,
                "id": row[0],
                "category": row[1],
                "region_name": row[2]
            }
        })
    return {
        "type": "FeatureCollection",
        "count": len(features),
        "features": features
    }