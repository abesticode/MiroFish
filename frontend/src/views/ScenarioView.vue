<template>
  <div class="scenario-container">
    <nav class="navbar">
      <div class="nav-brand" @click="$router.push('/')">MIROFISH</div>
      <div class="nav-links">
        <span class="nav-subtitle">Scenario Generator</span>
      </div>
    </nav>

    <div class="main-content">
      <div class="page-header">
        <div class="tag-row">
          <span class="orange-tag">CUSTOM PROFILE GENERATOR</span>
          <span class="version-text">/ scenario-based</span>
        </div>
        <h1 class="page-title">Generate Synthetic Agent Population</h1>
        <p class="page-desc">
          Buat populasi agent sintetis dari template skenario. Upload dokumen pendukung dan tulis simulation prompt untuk hasil prediksi yang lebih akurat.
        </p>
      </div>

      <div class="content-grid">
        <!-- Left: Configuration -->
        <div class="config-panel">
          <!-- Step 1: Choose Scenario -->
          <div class="config-section">
            <div class="section-header">
              <span class="step-num">01</span>
              <span class="section-label">Pilih Skenario</span>
            </div>
            <div v-if="loadingScenarios" class="loading-box">Loading scenarios...</div>
            <div v-else class="scenario-cards">
              <div
                v-for="s in scenarios"
                :key="s.name"
                class="scenario-card"
                :class="{ active: selectedScenario === s.name }"
                @click="selectScenario(s.name)"
              >
                <div class="card-name">{{ s.name }}</div>
                <div class="card-desc">{{ s.description }}</div>
              </div>
            </div>
          </div>

          <!-- Step 2: Upload Document (Optional) -->
          <div class="config-section">
            <div class="section-header">
              <span class="step-num">02</span>
              <span class="section-label">Real-world Seed</span>
              <span class="optional-tag">Opsional</span>
            </div>
            <div class="section-hint">Upload data pendukung: jadwal pertandingan, data historis rating, info paket, dll.</div>
            <div
              class="upload-zone"
              :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
              @dragover.prevent="isDragOver = true"
              @dragleave.prevent="isDragOver = false"
              @drop.prevent="handleDrop"
              @click="$refs.fileInput.click()"
            >
              <input
                ref="fileInput"
                type="file"
                multiple
                accept=".pdf,.md,.txt"
                @change="handleFileSelect"
                style="display: none"
                :disabled="generating"
              />
              <div v-if="files.length === 0" class="upload-placeholder">
                <div class="upload-icon">↑</div>
                <div class="upload-title">Drag & drop files here</div>
                <div class="upload-hint">PDF, MD, TXT — or click to browse</div>
              </div>
              <div v-else class="file-list">
                <div v-for="(file, index) in files" :key="index" class="file-item">
                  <span class="file-name">{{ file.name }}</span>
                  <button @click.stop="files.splice(index, 1)" class="remove-btn">x</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Simulation Prompt -->
          <div class="config-section">
            <div class="section-header">
              <span class="step-num">03</span>
              <span class="section-label">Simulation Prompt</span>
              <span class="optional-tag">Opsional</span>
            </div>
            <div class="section-hint">Deskripsikan tujuan simulasi dan prediksi yang ingin dihasilkan.</div>
            <div class="input-wrapper">
              <textarea
                v-model="simulationPrompt"
                class="code-input"
                placeholder="// Contoh: Simulasikan perilaku pengguna Maxstream dalam memilih pertandingan. Prediksi Top 10 pertandingan dengan jumlah penonton tertinggi beserta confidence score dan faktor yang berpengaruh."
                rows="8"
                :disabled="generating"
              ></textarea>
            </div>
          </div>

          <!-- Step 4: Parameters -->
          <div class="config-section">
            <div class="section-header">
              <span class="step-num">04</span>
              <span class="section-label">Parameter</span>
            </div>
            <div class="param-grid">
              <div class="param-item">
                <label>Jumlah Agent</label>
                <input type="number" v-model.number="params.total_agents" min="5" max="500" :disabled="generating" />
              </div>
              <div class="param-item">
                <label>Platform Output</label>
                <select v-model="params.platform" :disabled="generating">
                  <option value="reddit">Reddit (JSON)</option>
                  <option value="twitter">Twitter (CSV)</option>
                </select>
              </div>
              <div class="param-item">
                <label>Parallel Count</label>
                <input type="number" v-model.number="params.parallel_count" min="1" max="10" :disabled="generating" />
              </div>
              <div class="param-item">
                <label>Bahasa Simulasi</label>
                <select v-model="params.language" :disabled="generating">
                  <option value="id">Bahasa Indonesia</option>
                  <option value="en">English</option>
                  <option value="zh">中文</option>
                </select>
              </div>
              <div class="param-item toggle-item">
                <label>Gunakan LLM</label>
                <div class="toggle-wrapper">
                  <button class="toggle-btn" :class="{ on: params.use_llm }" @click="params.use_llm = !params.use_llm" :disabled="generating">
                    {{ params.use_llm ? 'ON' : 'OFF' }}
                  </button>
                  <span class="toggle-hint">{{ params.use_llm ? 'Persona detail dari LLM' : 'Rule-based (cepat)' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 5: Action -->
          <div class="config-section">
            <button class="generate-btn" :disabled="!selectedScenario || generating" @click="startGenerate">
              <span v-if="!generating">
                {{ simulationPrompt.trim() ? 'Generate + Run Simulation' : 'Generate Profiles Only' }}
              </span>
              <span v-else>{{ statusMessage }}</span>
              <span class="btn-arrow">→</span>
            </button>
          </div>

          <!-- Error -->
          <div v-if="error" class="error-box">{{ error }}</div>

          <!-- Result -->
          <div v-if="result" class="result-box">
            <div class="result-header">Generation Complete</div>
            <div class="result-stats">
              <div class="stat">
                <span class="stat-value">{{ result.total_generated }}</span>
                <span class="stat-label">Agents</span>
              </div>
              <div class="stat">
                <span class="stat-value">{{ selectedScenario }}</span>
                <span class="stat-label">Scenario</span>
              </div>
            </div>
            <div v-if="result.simulation_id" class="result-actions">
              <button class="action-btn primary" @click="goToSimulation(result.simulation_id)">
                Run Simulation →
              </button>
            </div>
            <div class="result-path">
              <span class="path-label">Output:</span>
              <code>{{ result.output_path || result.output_dir }}</code>
            </div>
          </div>
        </div>

        <!-- Right: Archetype Preview -->
        <div class="preview-panel">
          <div class="preview-header">
            <span class="diamond-icon">◇</span> Archetype Preview
          </div>
          <div v-if="!scenarioInfo" class="preview-empty">
            Pilih skenario untuk melihat detail archetype
          </div>
          <div v-else class="archetype-list">
            <div class="scenario-meta">
              <div class="meta-title">{{ scenarioInfo.name }}</div>
              <div class="meta-desc">{{ scenarioInfo.description }}</div>
              <div class="meta-demographics">
                <span>Country: {{ scenarioInfo.demographics.country }}</span>
                <span v-for="(pct, region) in scenarioInfo.demographics.regions" :key="region">
                  {{ region }}: {{ Math.round(pct * 100) }}%
                </span>
              </div>
            </div>
            <div v-for="arch in scenarioInfo.archetypes" :key="arch.key" class="archetype-card">
              <div class="arch-header">
                <span class="arch-label">{{ arch.label }}</span>
                <span class="arch-pct">{{ Math.round(arch.percentage * 100) }}%</span>
              </div>
              <div class="arch-desc">{{ arch.description }}</div>
              <div class="arch-meta">
                <span>Age: {{ arch.age_range[0] }}-{{ arch.age_range[1] }}</span>
                <span>Topics: {{ arch.interested_topics.slice(0, 3).join(', ') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listScenarios, getScenarioInfo, generateScenarioProfiles, generateScenarioWithSimulation } from '../api/simulation'
import service from '../api/index'

const router = useRouter()

const scenarios = ref([])
const selectedScenario = ref(null)
const scenarioInfo = ref(null)
const loadingScenarios = ref(true)
const generating = ref(false)
const statusMessage = ref('Generating...')
const error = ref('')
const result = ref(null)

const files = ref([])
const isDragOver = ref(false)
const simulationPrompt = ref('')

const params = ref({
  total_agents: 50,
  use_llm: true,
  parallel_count: 5,
  platform: 'reddit',
  language: 'id',
})

onMounted(async () => {
  try {
    const res = await listScenarios()
    scenarios.value = res.data
  } catch (e) {
    error.value = 'Failed to load scenarios: ' + (e.message || e)
  } finally {
    loadingScenarios.value = false
  }
})

const selectScenario = async (name) => {
  selectedScenario.value = name
  scenarioInfo.value = null
  error.value = ''
  result.value = null
  try {
    const res = await getScenarioInfo(name)
    scenarioInfo.value = res.data
  } catch (e) {
    error.value = 'Failed to load scenario info: ' + (e.message || e)
  }
}

const handleFileSelect = (event) => {
  const selected = Array.from(event.target.files).filter(f => {
    const ext = f.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...selected)
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (generating.value) return
  const dropped = Array.from(e.dataTransfer.files).filter(f => {
    const ext = f.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...dropped)
}

const startGenerate = async () => {
  if (!selectedScenario.value || generating.value) return

  generating.value = true
  error.value = ''
  result.value = null

  const hasPrompt = simulationPrompt.value.trim()
  const hasFiles = files.value.length > 0

  try {
    if (hasFiles || hasPrompt) {
      // Use multipart endpoint that handles files + generation together
      statusMessage.value = 'Generating agents...'
      const formData = new FormData()
      formData.append('scenario_name', selectedScenario.value)
      formData.append('total_agents', params.value.total_agents)
      formData.append('use_llm', params.value.use_llm)
      formData.append('parallel_count', params.value.parallel_count)
      formData.append('platform', params.value.platform)
      formData.append('language', params.value.language)

      if (hasPrompt) {
        formData.append('simulation_requirement', simulationPrompt.value)
      }

      if (hasFiles) {
        files.value.forEach(f => formData.append('files', f))
      }

      const res = await service.post('/api/simulation/scenarios/generate-full', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 1800000,
      })
      result.value = res.data
    } else {
      // Generate profiles only (no files, no prompt)
      statusMessage.value = 'Generating agent profiles...'
      const res = await generateScenarioProfiles({
        scenario_name: selectedScenario.value,
        total_agents: params.value.total_agents,
        use_llm: params.value.use_llm,
        parallel_count: params.value.parallel_count,
        platform: params.value.platform,
      })
      result.value = res.data
    }

    statusMessage.value = 'Complete!'
  } catch (e) {
    error.value = 'Generation failed: ' + (e.message || e)
  } finally {
    generating.value = false
  }
}

const goToSimulation = (simulationId) => {
  router.push({ name: 'SimulationRun', params: { simulationId } })
}
</script>

<style scoped>
.scenario-container {
  min-height: 100vh;
  background: #FFFFFF;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  color: #000000;
}

.navbar {
  height: 60px;
  background: #000000;
  color: #FFFFFF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.2rem;
  cursor: pointer;
}

.nav-subtitle {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  opacity: 0.7;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px;
}

.page-header { margin-bottom: 40px; }

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
}

.orange-tag {
  background: #FF4500;
  color: #FFFFFF;
  padding: 4px 10px;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 0.75rem;
}

.version-text { color: #999; font-weight: 500; }

.page-title {
  font-size: 2.5rem;
  font-weight: 500;
  margin: 0 0 10px 0;
  letter-spacing: -1px;
}

.page-desc {
  color: #666666;
  font-size: 1rem;
  line-height: 1.6;
  max-width: 700px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 40px;
  align-items: start;
}

.config-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-section {
  border: 1px solid #E5E5E5;
  padding: 25px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #000000;
  opacity: 0.3;
  font-size: 0.9rem;
}

.section-label { font-weight: 520; font-size: 1rem; }

.optional-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: #999;
  border: 1px solid #DDD;
  padding: 2px 6px;
  letter-spacing: 0.5px;
}

.section-hint {
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 12px;
}

.loading-box {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: #999;
  padding: 20px;
  text-align: center;
}

.scenario-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.scenario-card {
  border: 1px solid #E5E5E5;
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.scenario-card:hover { border-color: #999; background: #FAFAFA; }
.scenario-card.active { border-color: #FF4500; background: #FFF8F5; }

.card-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.card-desc { font-size: 0.85rem; color: #666666; }

/* Upload zone */
.upload-zone {
  border: 1px dashed #CCC;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #FAFAFA;
}

.upload-zone.has-files { align-items: flex-start; }
.upload-zone:hover { background: #F0F0F0; border-color: #999; }
.upload-zone.drag-over { border-color: #FF4500; background: #FFF8F5; }

.upload-placeholder { text-align: center; padding: 20px; }
.upload-icon { width: 30px; height: 30px; border: 1px solid #DDD; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; color: #999; }
.upload-title { font-weight: 500; font-size: 0.85rem; margin-bottom: 4px; }
.upload-hint { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #999; }

.file-list { width: 100%; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #FFF;
  padding: 8px 12px;
  border: 1px solid #EEE;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
}

.remove-btn { background: none; border: none; cursor: pointer; font-size: 1rem; color: #999; }
.remove-btn:hover { color: #FF4500; }

/* Textarea */
.input-wrapper { border: 1px solid #DDD; background: #FAFAFA; }

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 15px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 140px;
}

/* Parameters */
.param-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.param-item { display: flex; flex-direction: column; gap: 6px; }
.param-item label { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #999; }
.param-item input, .param-item select {
  border: 1px solid #DDD;
  padding: 10px 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  background: #FAFAFA;
  outline: none;
}
.param-item input:focus, .param-item select:focus { border-color: #000; }

.toggle-item { grid-column: span 2; }
.toggle-wrapper { display: flex; align-items: center; gap: 12px; }
.toggle-btn {
  padding: 8px 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  font-weight: 700;
  border: 1px solid #DDD;
  background: #F5F5F5;
  cursor: pointer;
  transition: all 0.2s;
}
.toggle-btn.on { background: #000; color: #FFF; border-color: #000; }
.toggle-hint { font-size: 0.8rem; color: #999; }

/* Generate button */
.generate-btn {
  width: 100%;
  background: #000000;
  color: #FFFFFF;
  border: 1px solid #000000;
  padding: 18px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
  letter-spacing: 0.5px;
}
.generate-btn:hover:not(:disabled) { background: #FF4500; border-color: #FF4500; }
.generate-btn:disabled { background: #E5E5E5; color: #999; cursor: not-allowed; border-color: #E5E5E5; }
.btn-arrow { font-size: 1.2rem; }

/* Error & Result */
.error-box {
  background: #FFF0F0;
  border: 1px solid #FFD0D0;
  padding: 15px 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: #CC0000;
}

.result-box {
  border: 1px solid #00AA00;
  background: #F0FFF0;
  padding: 20px;
}

.result-header {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1rem;
  color: #00AA00;
  margin-bottom: 15px;
}

.result-stats { display: flex; gap: 25px; margin-bottom: 15px; flex-wrap: wrap; }
.stat { display: flex; flex-direction: column; }
.stat-value { font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; }
.stat-label { font-size: 0.75rem; color: #666; }

.result-actions { margin-bottom: 15px; }
.action-btn {
  background: #000;
  color: #FFF;
  border: none;
  padding: 10px 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.action-btn:hover { background: #FF4500; }
.action-btn.primary {
  width: 100%;
  padding: 16px;
  font-size: 1rem;
  letter-spacing: 0.5px;
}

.result-path { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #666; }
.result-path code { display: block; margin-top: 5px; background: #F5F5F5; padding: 8px; word-break: break-all; font-size: 0.7rem; }

/* Preview Panel */
.preview-panel {
  border: 1px solid #E5E5E5;
  padding: 25px;
  position: sticky;
  top: 20px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}

.preview-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon { font-size: 1.2rem; }

.preview-empty { text-align: center; padding: 40px; color: #999; font-size: 0.9rem; }

.scenario-meta { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #E5E5E5; }
.meta-title { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.1rem; margin-bottom: 5px; }
.meta-desc { font-size: 0.85rem; color: #666; margin-bottom: 10px; }
.meta-demographics { display: flex; flex-wrap: wrap; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #999; }
.meta-demographics span { background: #F5F5F5; padding: 3px 8px; border: 1px solid #EEE; }

.archetype-list { display: flex; flex-direction: column; gap: 15px; }

.archetype-card { border: 1px solid #E5E5E5; padding: 15px; transition: border-color 0.2s; }
.archetype-card:hover { border-color: #FF4500; }

.arch-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.arch-label { font-weight: 600; font-size: 0.95rem; }
.arch-pct { font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #FF4500; font-size: 0.9rem; }
.arch-desc { font-size: 0.8rem; color: #666; line-height: 1.5; margin-bottom: 10px; }
.arch-meta { display: flex; flex-wrap: wrap; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #999; }
.arch-meta span { background: #F5F5F5; padding: 2px 6px; }

@media (max-width: 1024px) {
  .content-grid { grid-template-columns: 1fr; }
  .preview-panel { position: static; max-height: none; }
}
</style>
