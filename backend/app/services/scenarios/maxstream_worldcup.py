"""
Maxstream World Cup Scenario

Simulates Telkomsel Maxstream viewers during FIFA World Cup matches.
Used to predict which matches will have the highest viewership on the platform.

Archetypes based on Indonesian football fandom behavior:
- Fans Garis Keras (Hardcore Fan)
- Fans Musiman / FOMO (Casual Viewer)
- Anak Nobar (Social Watcher)
- Pecinta Skor (Bettor/Pundit Amatir)
"""

import random
from typing import Dict, Any, List, Optional
from dataclasses import field

from .base import (
    SimulationScenario,
    Archetype,
    DemographicDistribution,
    DemographicSample,
    register_scenario,
)


@register_scenario
class MaxstreamWorldCupScenario(SimulationScenario):
    name = "maxstream_worldcup"
    description = "Simulasi penonton Piala Dunia di platform Maxstream Telkomsel"

    # Access type distribution (assigned as extra_attribute)
    ACCESS_TYPES = {
        "kuota_hunter": 0.40,
        "wifi_indihome": 0.35,
        "mobile_commuter": 0.25,
    }

    ACCESS_TYPE_LABELS = {
        "kuota_hunter": "Kuota Hunter (Paket Nonton Bola)",
        "wifi_indihome": "Pengguna Wi-Fi / IndiHome",
        "mobile_commuter": "Mobile-First Commuter",
    }

    # Region (timezone) distribution
    REGIONS = {
        "WIB (Jakarta/Bandung/Sumatera)": 0.60,
        "WITA (Bali/Sulawesi/Kalimantan)": 0.25,
        "WIT (Papua/Maluku)": 0.15,
    }

    # Login behavior patterns
    LOGIN_PATTERNS = {
        "standby_30min": "Standby 30 menit sebelum kick-off, sudah buka app dan set reminder",
        "early_5min": "Buka app 5 menit sebelum kick-off, sudah siap di home screen",
        "reactive_post_goal": "Buka app setelah lihat Twitter/X ramai ada gol (5-10 menit setelah kick-off)",
        "halftime_joiner": "Join saat halftime karena penasaran skor, lalu stay nonton babak 2",
    }

    def get_archetypes(self) -> List[Archetype]:
        return [
            Archetype(
                key="hardcore_fan",
                label="Fans Garis Keras",
                description=(
                    "Menonton hampir semua pertandingan termasuk jam 2 pagi. Hafal statistik pemain, "
                    "setia pada satu tim nasional favorit. Selalu buka Maxstream walau "
                    "graveyard shift. Sangat sensitif terhadap buffering karena sudah bayar paket khusus. "
                    "Tipe yang bikin thread live commentary di Twitter saat nonton."
                ),
                percentage=0.25,
                age_range=(18, 40),
                gender_distribution={"male": 0.85, "female": 0.15},
                professions=[
                    "Mahasiswa", "Pekerja IT", "Freelancer", "Wiraswasta",
                    "Content Creator", "Barista", "Ojol Driver"
                ],
                interested_topics=[
                    "Highlights Gol & Cuplikan Pertandingan",
                    "Statistik & Analisis Taktik",
                    "Transfer Pemain & Rumor",
                    "Jersey & Merchandise Original",
                    "Fantasy Football",
                ],
                mbti_pool=["ENTJ", "ENTP", "ESTP", "ISTP", "INTJ", "ESTJ"],
                extra_attributes={
                    "viewing_commitment": "very_high",
                    "graveyard_tolerance": True,
                    "buffering_tolerance": "very_low",
                    "login_pattern": "standby_30min",
                    "watch_duration": "full_match",
                    "dropout_on_buffering": False,
                },
            ),
            Archetype(
                key="casual_fomo",
                label="Fans Musiman / FOMO",
                description=(
                    "Hanya menonton karena FOMO di media sosial. Biasa hanya nonton pertandingan "
                    "Prime Time (20:00-22:00 WIB) atau laga krusial (Semi Final & Final). "
                    "Skip pertandingan dini hari di hari kerja kecuali final. "
                    "Sering posting Instagram Story saat nonton untuk flex."
                ),
                percentage=0.35,
                age_range=(20, 45),
                gender_distribution={"male": 0.60, "female": 0.40},
                professions=[
                    "Pekerja Kantoran", "PNS", "Guru", "Karyawan Swasta",
                    "Ibu Rumah Tangga", "Mahasiswa", "Marketing"
                ],
                interested_topics=[
                    "Highlights Gol & Cuplikan Pertandingan",
                    "Meme Bola & Trolling Fans Lawan",
                    "Promo Kuota Telkomsel / Paket Data Murah",
                    "Tebak Skor Berhadiah",
                ],
                mbti_pool=["ESFP", "ENFP", "ESFJ", "ENFJ", "ISFP", "INFP"],
                extra_attributes={
                    "viewing_commitment": "medium",
                    "graveyard_tolerance": False,
                    "buffering_tolerance": "medium",
                    "skip_conditions": ["hari_kerja + jam_02", "tim_gurem", "fase_grup_awal"],
                    "login_pattern": "reactive_post_goal",
                    "watch_duration": "partial_or_highlights",
                    "dropout_on_buffering": True,
                },
            ),
            Archetype(
                key="anak_nobar",
                label="Anak Nobar (Social Watcher)",
                description=(
                    "Lebih suka nonton bersama di warkop, kafe, atau rumah teman. "
                    "Jika terpaksa nonton di app, biasanya share screen atau satu akun ramai-ramai. "
                    "Pengalaman nonton = pengalaman sosial, bukan soal pertandingannya. "
                    "Sering pesan makanan/minuman saat nonton, bikin konten TikTok reaction."
                ),
                percentage=0.20,
                age_range=(17, 30),
                gender_distribution={"male": 0.65, "female": 0.35},
                professions=[
                    "Mahasiswa", "Pelajar SMA", "Pekerja Part-time",
                    "Barista", "Ojol Driver", "Karyawan Retail"
                ],
                interested_topics=[
                    "Meme Bola & Trolling Fans Lawan",
                    "Highlights Gol & Cuplikan Pertandingan",
                    "Lokasi Nobar Terdekat",
                    "Promo Kuota Telkomsel / Paket Data Murah",
                    "Reaction Video & TikTok",
                ],
                mbti_pool=["ESFP", "ENFP", "ESTP", "ENTP", "ESFJ"],
                extra_attributes={
                    "viewing_commitment": "social_dependent",
                    "graveyard_tolerance": True,  # mau begadang kalau rame-rame
                    "buffering_tolerance": "high",  # yang penting rame
                    "login_pattern": "early_5min",
                    "watch_duration": "depends_on_group",
                    "shared_viewing": True,
                    "actual_viewers_per_account": (2, 5),
                    "dropout_on_buffering": False,
                },
            ),
            Archetype(
                key="bettor_pundit",
                label="Pecinta Skor (Bettor/Pundit Amatir)",
                description=(
                    "Menonton pertandingan apa saja termasuk negara gurem karena ada kepentingan "
                    "tebak skor atau taruhan kecil-kecilan. Tingkat retensi app sangat tinggi. "
                    "Sering switch antar pertandingan yang tayang bersamaan. "
                    "Hafal odds dan head-to-head record. Punya grup WA khusus prediksi bola."
                ),
                percentage=0.20,
                age_range=(22, 50),
                gender_distribution={"male": 0.92, "female": 0.08},
                professions=[
                    "Wiraswasta", "Pekerja Kantoran", "Pedagang",
                    "Ojol Driver", "Freelancer", "Buruh"
                ],
                interested_topics=[
                    "Tebak Skor & Analisis Taktik",
                    "Statistik Head-to-Head",
                    "Highlights Gol & Cuplikan Pertandingan",
                    "Odds & Prediksi Pertandingan",
                    "Multi-match Switching",
                ],
                mbti_pool=["ISTP", "INTP", "ESTP", "ENTJ", "ISTJ", "INTJ"],
                extra_attributes={
                    "viewing_commitment": "very_high",
                    "graveyard_tolerance": True,
                    "buffering_tolerance": "low",
                    "watches_any_match": True,
                    "login_pattern": "standby_30min",
                    "watch_duration": "multi_match_switching",
                    "dropout_on_buffering": False,
                    "app_retention": "very_high",
                },
            ),
        ]

    def get_demographic_distribution(self) -> DemographicDistribution:
        return DemographicDistribution(
            country="Indonesia",
            regions=self.REGIONS,
            age_range=(17, 50),
            gender_distribution={"male": 0.75, "female": 0.25},
            extra={
                "access_types": self.ACCESS_TYPES,
                "platform": "Maxstream (Telkomsel)",
                "event": "FIFA World Cup",
                "prime_time_hours": [20, 21, 22, 23],
                "graveyard_hours": [0, 1, 2, 3, 4],
            },
        )

    def sample_demographic(self, archetype: Archetype, demographics: DemographicDistribution) -> DemographicSample:
        """Override to add access_type sampling."""
        sample = super().sample_demographic(archetype, demographics)

        # Sample access type
        access_roll = random.random()
        cumulative = 0.0
        access_type = "kuota_hunter"
        for at, prob in self.ACCESS_TYPES.items():
            cumulative += prob
            if access_roll <= cumulative:
                access_type = at
                break

        sample.extra["access_type"] = access_type
        sample.extra["access_type_label"] = self.ACCESS_TYPE_LABELS[access_type]

        # Sample login pattern from archetype or random
        login_pattern = archetype.extra_attributes.get("login_pattern", "early_5min")
        sample.extra["login_pattern"] = login_pattern
        sample.extra["login_pattern_desc"] = self.LOGIN_PATTERNS.get(login_pattern, "")

        return sample

    def build_persona_prompt(self, archetype: Archetype, sample: DemographicSample, index: int) -> str:
        """Build detailed prompt for Indonesian Maxstream viewer persona."""

        access_label = sample.extra.get("access_type_label", "Pengguna Umum")
        login_desc = sample.extra.get("login_pattern_desc", "")

        return f"""Buatkan profil pengguna Maxstream (platform streaming Telkomsel) yang sangat detail dan realistis untuk simulasi penonton Piala Dunia.

Tipe Penonton: {archetype.label}
Deskripsi Tipe: {archetype.description}

Data Demografis:
- Usia: {sample.age} tahun
- Gender: {sample.gender}
- Wilayah/Zona Waktu: {sample.region}
- Profesi: {sample.profession}
- MBTI: {sample.mbti}
- Tipe Akses: {access_label}
- Pola Login: {login_desc}

Hasilkan JSON dengan field berikut:

1. "name": Nama Indonesia yang realistis sesuai gender (contoh: Budi Santoso, Dewi Lestari)
2. "bio": Deskripsi singkat 50-100 kata tentang kebiasaan nonton bola dan penggunaan Maxstream
3. "persona": Deskripsi sangat detail (800-1500 kata) yang HARUS mencakup:
   - Latar belakang: profesi, rutinitas harian, kondisi ekonomi
   - Kebiasaan nonton bola: tim favorit, sejarah nonton Piala Dunia, ritual sebelum nonton
   - Perilaku di Maxstream: kapan buka app, toleransi buffering, resolusi yang dipilih, durasi nonton
   - Pola jam nonton: apakah sanggup begadang (graveyard 02:00 WIB), preferensi prime time
   - Decision logic: kondisi apa yang membuat SKIP nonton vs PASTI nonton
   - Perilaku sosial media saat nonton: live tweet, IG story, grup WA
   - Sensitivitas paket data: pakai kuota khusus bola atau Wi-Fi, reaksi saat kuota habis
   - Interaksi dengan konten: nonton highlights saja atau full match, multi-match switching
4. "age": {sample.age}
5. "gender": "{sample.gender}"
6. "mbti": "{sample.mbti}"
7. "country": "Indonesia"
8. "profession": "{sample.profession}"
9. "interested_topics": array topik ketertarikan (gunakan bahasa Indonesia)

PENTING:
- Semua value harus string atau number, TIDAK boleh ada newline dalam string
- persona harus coherent text tanpa line break
- Gunakan Bahasa Indonesia untuk bio dan persona
- Nama harus realistis Indonesia
- Konten harus konsisten dengan tipe penonton "{archetype.label}" dan zona waktu {sample.region}
- age harus integer, gender harus "male" atau "female"
"""

    def build_rule_based_profile(self, archetype: Archetype, sample: DemographicSample, index: int) -> Dict[str, Any]:
        """Generate rule-based profile for Maxstream viewer."""

        first_names_male = [
            "Budi", "Andi", "Rizky", "Fajar", "Dimas", "Arif", "Hendra", "Wahyu",
            "Bagus", "Yoga", "Rendi", "Agus", "Eko", "Surya", "Bayu", "Gilang",
            "Aditya", "Faisal", "Irfan", "Joko", "Kevin", "Rafi", "Tegar", "Dani"
        ]
        first_names_female = [
            "Dewi", "Sari", "Putri", "Rina", "Ani", "Sri", "Wulan", "Mega",
            "Dian", "Fitri", "Nurul", "Ayu", "Indah", "Ratna", "Lestari", "Citra",
            "Nadia", "Tiara", "Zahra", "Intan", "Maya", "Rini", "Sinta", "Vina"
        ]
        last_names = [
            "Santoso", "Wijaya", "Pratama", "Hidayat", "Kusuma", "Saputra",
            "Nugroho", "Ramadhan", "Putra", "Setiawan", "Wibowo", "Firmansyah",
            "Permana", "Hakim", "Maulana", "Syahputra", "Fadillah", "Anggara"
        ]

        if sample.gender == "male":
            name = f"{random.choice(first_names_male)} {random.choice(last_names)}"
        else:
            name = f"{random.choice(first_names_female)} {random.choice(last_names)}"

        access_label = sample.extra.get("access_type_label", "Pengguna Umum")

        bio_templates = {
            "hardcore_fan": f"Fans berat sepakbola, nonton semua pertandingan di Maxstream termasuk jam 2 pagi. {access_label}. Zona {sample.region}.",
            "casual_fomo": f"Nonton Piala Dunia kalau lagi rame di timeline. Preferensi prime time. {access_label}. Zona {sample.region}.",
            "anak_nobar": f"Lebih suka nobar bareng teman di warkop. Pakai Maxstream kalau nggak bisa keluar. {access_label}. Zona {sample.region}.",
            "bettor_pundit": f"Nonton semua pertandingan untuk tebak skor. Hafal statistik dan odds. {access_label}. Zona {sample.region}.",
        }

        persona_templates = {
            "hardcore_fan": (
                f"{name} adalah seorang {sample.profession} berusia {sample.age} tahun di wilayah {sample.region}. "
                f"Sebagai fans garis keras sepakbola, dia tidak pernah melewatkan satu pertandingan pun di Piala Dunia. "
                f"Menggunakan Maxstream dengan paket {access_label}, biasanya sudah standby 30 menit sebelum kick-off. "
                f"Sangat tidak toleran terhadap buffering karena sudah membayar paket khusus. "
                f"Sanggup begadang untuk pertandingan jam 2 pagi WIB meskipun besoknya harus bekerja. "
                f"Aktif live tweet dan diskusi di grup WhatsApp fans selama pertandingan berlangsung. "
                f"Selalu nonton full match dari awal sampai akhir, tidak pernah cuma nonton highlights."
            ),
            "casual_fomo": (
                f"{name} adalah seorang {sample.profession} berusia {sample.age} tahun di wilayah {sample.region}. "
                f"Menonton Piala Dunia karena semua orang membicarakannya di media sosial. "
                f"Hanya nonton pertandingan prime time (20:00-22:00 WIB) atau laga-laga besar seperti Semi Final dan Final. "
                f"Menggunakan {access_label} untuk akses Maxstream. "
                f"Skip pertandingan dini hari di hari kerja, kecuali final atau ada gol viral di timeline. "
                f"Sering posting Instagram Story saat nonton sebagai konten sosial media. "
                f"Toleransi buffering sedang - kalau buffer lebih dari 30 detik biasanya pindah ke highlights."
            ),
            "anak_nobar": (
                f"{name} adalah seorang {sample.profession} berusia {sample.age} tahun di wilayah {sample.region}. "
                f"Bagi dia, nonton bola adalah pengalaman sosial. Lebih suka nobar di warkop atau rumah teman. "
                f"Menggunakan Maxstream dengan {access_label} hanya kalau tidak bisa keluar rumah. "
                f"Saat nonton di app, sering share screen atau nonton bareng 2-4 orang dari satu HP. "
                f"Sanggup begadang kalau nobar rame-rame, tapi malas nonton sendiri jam 2 pagi. "
                f"Sering bikin konten TikTok reaction saat gol atau momen lucu. "
                f"Tidak terlalu peduli buffering selama suasana nobar tetap seru."
            ),
            "bettor_pundit": (
                f"{name} adalah seorang {sample.profession} berusia {sample.age} tahun di wilayah {sample.region}. "
                f"Menonton semua pertandingan termasuk negara-negara gurem karena selalu pasang tebak skor. "
                f"Menggunakan Maxstream dengan {access_label}, retention rate sangat tinggi. "
                f"Sering multi-match switching kalau ada 2 pertandingan bersamaan. "
                f"Hafal odds, statistik head-to-head, dan performa pemain. "
                f"Punya grup WhatsApp khusus prediksi bola dengan 50+ anggota. "
                f"Nonton dari awal sampai akhir karena setiap gol dan kartu mempengaruhi prediksi."
            ),
        }

        return {
            "name": name,
            "bio": bio_templates.get(archetype.key, f"Penonton Maxstream dari {sample.region}."),
            "persona": persona_templates.get(archetype.key, f"{name} menonton Piala Dunia di Maxstream."),
            "age": sample.age,
            "gender": sample.gender,
            "mbti": sample.mbti,
            "country": "Indonesia",
            "profession": sample.profession,
            "interested_topics": archetype.interested_topics,
        }
