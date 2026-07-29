"""
CapCut + Telkomsel Bundle Scenario

Simulates potential buyers of a CapCut Pro + Telkomsel data bundle package.
Used to predict whether a bundled package would be profitable before launch.

Archetypes based on Indonesian content creator and consumer behavior:
- Kreator Aktif (Active Creator)
- Kreator Pemula (Beginner Creator)
- Konsumer Konten (Content Consumer)
- Power User
"""

import random
from typing import Dict, Any, List, Optional

from .base import (
    SimulationScenario,
    Archetype,
    DemographicDistribution,
    DemographicSample,
    register_scenario,
)


@register_scenario
class CapCutBundleScenario(SimulationScenario):
    name = "capcut_bundle"
    description = "Simulasi potensi pembelian paket bundling CapCut Pro + Telkomsel"

    REGIONS = {
        "WIB (Jakarta/Bandung/Sumatera)": 0.55,
        "WITA (Bali/Sulawesi/Kalimantan)": 0.28,
        "WIT (Papua/Maluku)": 0.17,
    }

    PRICE_SENSITIVITY = {
        "sangat_sensitif": 0.40,
        "moderat": 0.35,
        "tidak_sensitif": 0.25,
    }

    PRICE_SENSITIVITY_LABELS = {
        "sangat_sensitif": "Sangat sensitif harga, cari gratisan atau trial dulu",
        "moderat": "Mau bayar kalau value jelas dan ada promo",
        "tidak_sensitif": "Langsung beli kalau butuh, tidak mikir lama",
    }

    def get_archetypes(self) -> List[Archetype]:
        return [
            Archetype(
                key="kreator_aktif",
                label="Kreator Aktif",
                description=(
                    "Sudah pakai CapCut hampir setiap hari untuk edit konten TikTok/Reels/YouTube Shorts. "
                    "Familiar dengan fitur-fitur pro seperti keyframe, green screen, dan efek premium. "
                    "Langsung tertarik kalau ada bundling yang lebih murah dari beli terpisah. "
                    "Posting konten minimal 3-5x seminggu. Monetisasi atau sedang membangun audiens."
                ),
                percentage=0.25,
                age_range=(18, 32),
                gender_distribution={"male": 0.45, "female": 0.55},
                professions=[
                    "Content Creator", "Influencer", "Social Media Manager",
                    "Freelance Video Editor", "Mahasiswa Komunikasi",
                    "Owner Online Shop", "Food Blogger"
                ],
                interested_topics=[
                    "Tutorial Editing Video",
                    "Trend TikTok & Reels",
                    "Monetisasi Konten",
                    "Template & Efek Premium",
                    "Promo Paket Data Murah",
                    "Kamera HP & Gadget Review",
                ],
                mbti_pool=["ENFP", "ENTP", "ESFP", "ENTJ", "ENFJ"],
                extra_attributes={
                    "capcut_usage": "daily",
                    "content_frequency": "3-5x/minggu",
                    "monetization": True,
                    "price_sensitivity": "moderat",
                    "feature_awareness": "high",
                    "purchase_likelihood": "very_high",
                    "current_subscription": "trial_or_free",
                },
            ),
            Archetype(
                key="kreator_pemula",
                label="Kreator Pemula",
                description=(
                    "Baru mulai coba-coba edit video, tertarik jadi content creator tapi belum konsisten. "
                    "Pakai CapCut versi gratis, kadang frustrasi dengan watermark atau fitur terbatas. "
                    "Sangat sensitif harga - mau upgrade kalau ada trial gratis atau harga promo. "
                    "Posting konten 1-2x seminggu, masih eksperimen format dan gaya."
                ),
                percentage=0.30,
                age_range=(16, 28),
                gender_distribution={"male": 0.40, "female": 0.60},
                professions=[
                    "Mahasiswa", "Pelajar SMA", "Karyawan Muda",
                    "Fresh Graduate", "Part-timer", "Admin Medsos UMKM"
                ],
                interested_topics=[
                    "Tutorial Editing Video Pemula",
                    "Cara Dapat FYP TikTok",
                    "Template Gratis CapCut",
                    "Promo Paket Data Murah",
                    "Gadget Murah untuk Konten",
                    "Cara Monetisasi Pertama",
                ],
                mbti_pool=["INFP", "ISFP", "ENFP", "ESFP", "INFJ", "ISFJ"],
                extra_attributes={
                    "capcut_usage": "2-3x/minggu",
                    "content_frequency": "1-2x/minggu",
                    "monetization": False,
                    "price_sensitivity": "sangat_sensitif",
                    "feature_awareness": "medium",
                    "purchase_likelihood": "medium",
                    "current_subscription": "free_only",
                    "barrier": "harga_dan_belum_yakin_value",
                },
            ),
            Archetype(
                key="konsumer_konten",
                label="Konsumer Konten",
                description=(
                    "Pengguna TikTok/Reels aktif tapi sebagai penonton, bukan kreator. "
                    "Jarang atau tidak pernah edit video. Belum tentu butuh CapCut Pro. "
                    "Mungkin tertarik hanya kalau bundling paket datanya sangat murah. "
                    "Keputusan beli berbasis value paket data, bukan fitur CapCut."
                ),
                percentage=0.35,
                age_range=(16, 45),
                gender_distribution={"male": 0.50, "female": 0.50},
                professions=[
                    "Karyawan Swasta", "PNS", "Mahasiswa", "Pelajar",
                    "Ibu Rumah Tangga", "Pedagang", "Buruh", "Ojol Driver"
                ],
                interested_topics=[
                    "Promo Paket Data Murah",
                    "Konten Hiburan TikTok/Reels",
                    "Diskon & Cashback",
                    "Gosip & Trending Topic",
                    "Masak & Resep Video",
                ],
                mbti_pool=["ISFJ", "ESFJ", "ISFP", "ESFP", "ISTJ", "ESTJ"],
                extra_attributes={
                    "capcut_usage": "rarely_or_never",
                    "content_frequency": "passive_consumer",
                    "monetization": False,
                    "price_sensitivity": "sangat_sensitif",
                    "feature_awareness": "low",
                    "purchase_likelihood": "low",
                    "decision_driver": "harga_paket_data_bukan_capcut",
                },
            ),
            Archetype(
                key="power_user",
                label="Power User",
                description=(
                    "Kreator profesional atau semi-profesional yang butuh fitur advanced CapCut. "
                    "Biasa pakai CapCut Pro atau alternatif berbayar (VN, Premiere Rush). "
                    "Mau bayar harga premium untuk fitur lengkap. Kurang sensitif harga. "
                    "Posting konten setiap hari, punya audiens signifikan, sudah monetisasi."
                ),
                percentage=0.10,
                age_range=(20, 38),
                gender_distribution={"male": 0.50, "female": 0.50},
                professions=[
                    "Full-time Content Creator", "Video Editor Profesional",
                    "Social Media Agency", "YouTuber", "Influencer",
                    "Brand Consultant", "Digital Marketing"
                ],
                interested_topics=[
                    "Fitur Pro & Update CapCut",
                    "Color Grading & Advanced Editing",
                    "Monetisasi Multi-Platform",
                    "Kolaborasi Brand & Endorsement",
                    "Kamera & Equipment Pro",
                    "AI Video Tools",
                ],
                mbti_pool=["ENTJ", "INTJ", "ENTP", "INTP", "ESTJ"],
                extra_attributes={
                    "capcut_usage": "daily_professional",
                    "content_frequency": "daily",
                    "monetization": True,
                    "price_sensitivity": "tidak_sensitif",
                    "feature_awareness": "very_high",
                    "purchase_likelihood": "high",
                    "current_subscription": "already_paying",
                    "alternative_tools": ["VN", "Premiere Rush", "DaVinci"],
                },
            ),
        ]

    def get_demographic_distribution(self) -> DemographicDistribution:
        return DemographicDistribution(
            country="Indonesia",
            regions=self.REGIONS,
            age_range=(16, 45),
            gender_distribution={"male": 0.45, "female": 0.55},
            extra={
                "price_sensitivity_dist": self.PRICE_SENSITIVITY,
                "platform": "Telkomsel (MyTelkomsel App)",
                "bundle_product": "CapCut Pro + Kuota Data",
                "target_market": "Pengguna Telkomsel usia 16-35 yang aktif di short-form video",
            },
        )

    def sample_demographic(self, archetype: Archetype, demographics: DemographicDistribution) -> DemographicSample:
        """Override to add price sensitivity and usage pattern."""
        sample = super().sample_demographic(archetype, demographics)

        # Use archetype-defined sensitivity or sample from distribution
        arch_sensitivity = archetype.extra_attributes.get("price_sensitivity", None)
        if arch_sensitivity:
            sample.extra["price_sensitivity"] = arch_sensitivity
        else:
            roll = random.random()
            cumulative = 0.0
            sensitivity = "moderat"
            for s, prob in self.PRICE_SENSITIVITY.items():
                cumulative += prob
                if roll <= cumulative:
                    sensitivity = s
                    break
            sample.extra["price_sensitivity"] = sensitivity

        sample.extra["price_sensitivity_label"] = self.PRICE_SENSITIVITY_LABELS.get(
            sample.extra["price_sensitivity"], ""
        )
        sample.extra["capcut_usage"] = archetype.extra_attributes.get("capcut_usage", "unknown")
        sample.extra["purchase_likelihood"] = archetype.extra_attributes.get("purchase_likelihood", "unknown")

        return sample

    def build_persona_prompt(self, archetype: Archetype, sample: DemographicSample, index: int) -> str:
        """Build prompt for CapCut bundle potential buyer persona."""

        price_label = sample.extra.get("price_sensitivity_label", "")
        capcut_usage = sample.extra.get("capcut_usage", "unknown")
        purchase_likelihood = sample.extra.get("purchase_likelihood", "unknown")

        return f"""Buatkan profil pengguna Telkomsel yang sangat detail dan realistis untuk simulasi potensi pembelian paket bundling CapCut Pro + Kuota Data.

Tipe Pengguna: {archetype.label}
Deskripsi Tipe: {archetype.description}

Data Demografis:
- Usia: {sample.age} tahun
- Gender: {sample.gender}
- Wilayah: {sample.region}
- Profesi: {sample.profession}
- MBTI: {sample.mbti}
- Sensitivitas Harga: {price_label}
- Frekuensi Pakai CapCut: {capcut_usage}
- Kemungkinan Beli: {purchase_likelihood}

Hasilkan JSON dengan field berikut:

1. "name": Nama Indonesia yang realistis sesuai gender
2. "bio": Deskripsi singkat 50-100 kata tentang kebiasaan digital dan penggunaan CapCut/video editing
3. "persona": Deskripsi sangat detail (800-1500 kata) yang HARUS mencakup:
   - Latar belakang: profesi, penghasilan range, rutinitas digital harian
   - Kebiasaan konten: platform utama (TikTok/Reels/Shorts), frekuensi posting, jenis konten
   - Penggunaan CapCut: fitur yang sering dipakai, frustrasi dengan versi gratis, awareness fitur pro
   - Decision logic untuk pembelian paket bundling:
     * Harga berapa yang acceptable (range Rp)
     * Apa yang membuat BELI: diskon, trial gratis, rekomendasi teman, kebutuhan mendadak
     * Apa yang membuat SKIP: terlalu mahal, belum butuh, ada alternatif gratis
   - Perilaku paket data: rata-rata spending paket data per bulan, preferensi paket
   - Reaksi terhadap iklan/promo bundling di MyTelkomsel app
   - Pengaruh sosial: apakah decision dipengaruhi teman/influencer/review
4. "age": {sample.age}
5. "gender": "{sample.gender}"
6. "mbti": "{sample.mbti}"
7. "country": "Indonesia"
8. "profession": "{sample.profession}"
9. "interested_topics": array topik ketertarikan (bahasa Indonesia)

PENTING:
- Semua value harus string atau number, TIDAK boleh ada newline dalam string
- persona harus coherent text tanpa line break
- Gunakan Bahasa Indonesia untuk bio dan persona
- Nama harus realistis Indonesia
- Konten harus konsisten dengan tipe "{archetype.label}"
- age harus integer, gender harus "male" atau "female"
"""

    def build_rule_based_profile(self, archetype: Archetype, sample: DemographicSample, index: int) -> Dict[str, Any]:
        """Generate rule-based profile for CapCut bundle scenario."""

        first_names_male = [
            "Rizky", "Andi", "Dimas", "Kevin", "Rafi", "Fajar", "Gilang",
            "Aditya", "Yoga", "Bayu", "Faisal", "Dani", "Arya", "Bima", "Galih"
        ]
        first_names_female = [
            "Nadia", "Tiara", "Zahra", "Putri", "Sari", "Indah", "Citra",
            "Ayu", "Dian", "Fitri", "Maya", "Intan", "Rani", "Tasya", "Vina"
        ]
        last_names = [
            "Pratama", "Wijaya", "Santoso", "Hidayat", "Ramadhan", "Permana",
            "Saputra", "Kusuma", "Putra", "Setiawan", "Anggraini", "Lestari"
        ]

        if sample.gender == "male":
            name = f"{random.choice(first_names_male)} {random.choice(last_names)}"
        else:
            name = f"{random.choice(first_names_female)} {random.choice(last_names)}"

        price_label = sample.extra.get("price_sensitivity_label", "")

        bio_templates = {
            "kreator_aktif": (
                f"Content creator aktif, pakai CapCut setiap hari untuk edit konten TikTok/Reels. "
                f"Tertarik bundling kalau lebih murah dari langganan terpisah. {sample.region}."
            ),
            "kreator_pemula": (
                f"Baru belajar bikin konten video. Pakai CapCut gratis tapi sering keterbatasan fitur. "
                f"Sensitif harga, butuh promo menarik untuk upgrade. {sample.region}."
            ),
            "konsumer_konten": (
                f"Pengguna TikTok/Reels aktif sebagai penonton. Jarang edit video sendiri. "
                f"Tertarik bundling hanya kalau paket datanya worth it. {sample.region}."
            ),
            "power_user": (
                f"Kreator profesional, sudah pakai tools editing berbayar. Butuh fitur pro lengkap. "
                f"Langsung beli kalau value sesuai, tidak masalah dengan harga. {sample.region}."
            ),
        }

        persona_templates = {
            "kreator_aktif": (
                f"{name} adalah seorang {sample.profession} berusia {sample.age} tahun di wilayah {sample.region}. "
                f"Sudah aktif membuat konten video 3-5 kali seminggu di TikTok dan Instagram Reels. "
                f"Menggunakan CapCut setiap hari untuk editing, familiar dengan fitur keyframe, green screen, dan template. "
                f"Saat ini menggunakan versi gratis dan sering terganggu watermark. "
                f"Sensitivitas harga: {price_label}. "
                f"Sangat tertarik dengan bundling CapCut Pro + kuota data karena biasa habis kuota besar untuk upload konten. "
                f"Decision: akan beli kalau harga bundling lebih murah 20-30% dari beli terpisah."
            ),
            "kreator_pemula": (
                f"{name} adalah seorang {sample.profession} berusia {sample.age} tahun di wilayah {sample.region}. "
                f"Baru mulai eksperimen membuat konten video 1-2 kali seminggu, masih belajar teknik editing. "
                f"Pakai CapCut versi gratis, sering frustrasi dengan limitasi fitur dan watermark. "
                f"Sensitivitas harga: {price_label}. "
                f"Belum yakin apakah worth it untuk bayar, masih ragu apakah akan konsisten bikin konten. "
                f"Decision: akan beli kalau ada trial gratis 7-14 hari atau harga promo di bawah Rp 30.000/bulan. "
                f"Sangat terpengaruh rekomendasi teman atau influencer yang dia follow."
            ),
            "konsumer_konten": (
                f"{name} adalah seorang {sample.profession} berusia {sample.age} tahun di wilayah {sample.region}. "
                f"Pengguna aktif TikTok dan Instagram sebagai penonton, scroll konten 2-3 jam sehari. "
                f"Jarang atau tidak pernah edit video sendiri, belum merasa butuh CapCut Pro. "
                f"Sensitivitas harga: {price_label}. "
                f"Hanya akan tertarik bundling kalau paket datanya sangat murah atau ada bonus kuota besar. "
                f"Decision: fitur CapCut bukan faktor, yang dilihat murni value paket data vs harga. "
                f"Spending paket data rata-rata Rp 50.000-80.000/bulan."
            ),
            "power_user": (
                f"{name} adalah seorang {sample.profession} berusia {sample.age} tahun di wilayah {sample.region}. "
                f"Kreator profesional yang sudah menghasilkan uang dari konten. Posting setiap hari. "
                f"Biasa pakai CapCut Pro atau tools lain seperti VN, Premiere Rush. "
                f"Sensitivitas harga: {price_label}. "
                f"Sudah terbiasa bayar untuk tools profesional, spending digital Rp 200.000+/bulan. "
                f"Decision: akan beli bundling kalau bisa hemat dibanding langganan terpisah, "
                f"atau kalau ada fitur eksklusif bundling yang tidak ada di langganan biasa."
            ),
        }

        return {
            "name": name,
            "bio": bio_templates.get(archetype.key, f"Pengguna Telkomsel dari {sample.region}."),
            "persona": persona_templates.get(archetype.key, f"{name} menggunakan Telkomsel."),
            "age": sample.age,
            "gender": sample.gender,
            "mbti": sample.mbti,
            "country": "Indonesia",
            "profession": sample.profession,
            "interested_topics": archetype.interested_topics,
        }
