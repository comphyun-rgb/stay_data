from app.db import SessionLocal
from app.models.property_master import PropertyMaster
from app.models.property_entity import PropertyEntity
from sqlalchemy import func, text

def build_entity_layer():
    db = SessionLocal()
    try:
        # 1. 기존 엔티티 레이어 초기화 (재구축을 위함)
        db.query(PropertyEntity).delete()
        db.execute(text("UPDATE property_master SET entity_id = NULL"))
        db.commit()
        
        print("\n=== 엔티티 레이어 구축 시작 ===")
        
        # 2. 이름 + 주소 기준으로 그룹화하여 고유 숙소 식별
        # 공백 제거 및 소문자 변환하여 정교하게 매칭
        raw_list = db.query(PropertyMaster).all()
        
        groups = {}
        for item in raw_list:
            # 매칭 키 생성: (공백제거 이름, 공백제거 주소)
            name_key = (item.canonical_name or "").strip().replace(" ", "").lower()
            addr_key = (item.address_road or "").strip().replace(" ", "").lower()
            key = (name_key, addr_key)
            
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
            
        print(f"   - 총 원본 레코드: {len(raw_list)}건")
        print(f"   - 식별된 고유 엔티티: {len(groups)}건")
        
        # 3. 각 그룹별로 엔티티 생성 및 연결
        for key, members in groups.items():
            # 대표 멤버 선정 (가급적 좌표가 있는 건)
            representative = members[0]
            for m in members:
                if m.lat and m.lng:
                    representative = m
                    break
            
            new_entity = PropertyEntity(
                display_name=representative.canonical_name,
                representative_address=representative.address_road,
                district=representative.district_normalized or representative.district,
                cluster_area=representative.cluster_area,
                lat=representative.lat,
                lng=representative.lng,
                master_count=len(members)
            )
            db.add(new_entity)
            db.flush() # ID 생성을 위해 flush
            
            # 그룹 내 모든 멤버에게 엔티티 ID 부여
            for m in members:
                m.entity_id = new_entity.id
        
        db.commit()
        print("✅ 엔티티 레이어 구축 완료!")
        
    except Exception as e:
        print(f"❌ 엔티티 구축 중 오류: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    build_entity_layer()
