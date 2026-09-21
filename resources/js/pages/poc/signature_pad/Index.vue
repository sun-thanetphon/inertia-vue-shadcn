<script setup lang="ts">
import { ref, computed } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import SignaturePadCanvas from './SignaturePadCanvas.vue';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'vue-sonner';
import {
  PenTool,
  Download,
  FileCode,
  ShieldCheck,
  Smartphone,
  Tablet,
  Monitor,
  CheckCircle2,
  FileText,
  Activity,
  Layers,
  Sparkles,
  Info
} from '@lucide/vue';

defineOptions({
  layout: {
    breadcrumbs: [
      { title: 'Dashboard', href: '/dashboard' },
      { title: 'เซ็นชื่อดิจิทัล (signature_pad)', href: '/poc/signature' },
    ],
  },
});

const padRef = ref<InstanceType<typeof SignaturePadCanvas> | null>(null);

// Options
const penColor = ref('#0f172a');
const strokePreset = ref<'thin' | 'normal' | 'thick'>('normal');
const isDisabled = ref(false);

// Exported states
const signatureDataUrl = ref<string | null>(null);
const signatureSvg = ref<string | null>(null);
const pointGroupsCount = ref(0);
const totalPointsCount = ref(0);
const lastTimestamp = ref<string | null>(null);
const currentDpr = ref(typeof window !== 'undefined' ? window.devicePixelRatio : 1);

// Preset colors
const colorPresets = [
  { name: 'สีดำมาตรฐาน', value: '#0f172a', class: 'bg-slate-900 ring-slate-900' },
  { name: 'สีน้ำเงินคลินิก', value: '#1d4ed8', class: 'bg-blue-700 ring-blue-700' },
  { name: 'สีเขียวการแพทย์', value: '#059669', class: 'bg-emerald-600 ring-emerald-600' },
  { name: 'สีแดงตรวจสอบ', value: '#dc2626', class: 'bg-rose-600 ring-rose-600' },
];

const minMaxWidth = computed(() => {
  switch (strokePreset.value) {
    case 'thin':
      return { min: 0.8, max: 2.0 };
    case 'thick':
      return { min: 2.5, max: 5.5 };
    default:
      return { min: 1.5, max: 3.5 };
  }
});

const handleStrokeEnd = (payload: { dataUrl: string | null; isEmpty: boolean; pointGroups: any[] }) => {
  signatureDataUrl.value = payload.dataUrl;
  pointGroupsCount.value = payload.pointGroups.length;

  let points = 0;
  for (const group of payload.pointGroups) {
    if (group.points) {
      points += group.points.length;
    }
  }
  totalPointsCount.value = points;
  lastTimestamp.value = new Date().toLocaleTimeString('th-TH');
};

// Download helper
const downloadFile = (content: string, filename: string, isUrl = true) => {
  const link = document.createElement('a');
  link.href = isUrl ? content : `data:image/svg+xml;charset=utf-8,${encodeURIComponent(content)}`;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const handleDownloadPng = () => {
  const url = padRef.value?.toDataURL('image/png');
  if (!url) {
    toast.error('ยังไม่มีลายเซ็น กรุณาเซ็นชื่อก่อนดาวน์โหลด');
    return;
  }
  downloadFile(url, `signature_${Date.now()}.png`);
  toast.success('ดาวน์โหลดไฟล์ PNG (โปร่งใส) สำเร็จ');
};

const handleDownloadJpeg = () => {
  const url = padRef.value?.toDataURL('image/jpeg', 0.95);
  if (!url) {
    toast.error('ยังไม่มีลายเซ็น กรุณาเซ็นชื่อก่อนดาวน์โหลด');
    return;
  }
  downloadFile(url, `signature_${Date.now()}.jpg`);
  toast.success('ดาวน์โหลดไฟล์ JPEG (พื้นหลังขาว) สำเร็จ');
};

const handleDownloadSvg = () => {
  const svg = padRef.value?.toSVG();
  if (!svg) {
    toast.error('ยังไม่มีลายเซ็น กรุณาเซ็นชื่อก่อนดาวน์โหลด');
    return;
  }
  downloadFile(svg, `signature_${Date.now()}.svg`, false);
  toast.success('ดาวน์โหลดไฟล์ Vector SVG สำเร็จ (เหมาะสำหรับใบสั่งยา/ใบรับรองแพทย์)');
};

// Mock Inertia Form submission
const isSubmitting = ref(false);
const handleMockInertiaSubmit = () => {
  if (padRef.value?.isEmpty()) {
    toast.error('กรุณาลงลายเซ็นก่อนส่งเอกสาร');
    return;
  }

  isSubmitting.value = true;
  setTimeout(() => {
    isSubmitting.value = false;
    toast.success('บันทึกลายเซ็นและส่งเอกสารยินยอม (Consent Form) สำเร็จ!', {
      description: `Audit Trail: ${totalPointsCount.value} Points, ${pointGroupsCount.value} Strokes บันทึกเวลา ${lastTimestamp.value}`,
    });
  }, 900);
};
</script>

<template>
  <Head title="PoC: signature_pad (Enterprise Recommended)" />

  <div class="flex flex-col gap-6 p-4 md:p-8 max-w-7xl mx-auto w-full">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-5">
      <div class="space-y-1">
        <div class="flex items-center gap-2">
          <Badge variant="secondary" class="font-mono text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20">
            Enterprise Tier 1
          </Badge>
          <span class="text-xs text-muted-foreground">•</span>
          <span class="text-xs text-muted-foreground">ระบบลายเซ็นมาตรฐานของคลินิก</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
          <PenTool class="w-7 h-7 text-primary" />
          PoC: signature_pad (v5.1+)
        </h1>
        <p class="text-sm text-muted-foreground">
          โซลูชันระดับมาตรฐานสากล ใช้ W3C PointerEvents, รองรับ Apple Pencil, ป้องกันจอเลื่อนบน Mobile, และบันทึก Audit Biometric Trail
        </p>
      </div>

      <!-- Feature Badges -->
      <div class="flex flex-wrap items-center gap-1.5 self-start sm:self-auto">
        <Badge variant="outline" class="flex items-center gap-1 text-[11px] py-1">
          <Tablet class="w-3.5 h-3.5 text-blue-500" /> Apple Pencil / S-Pen
        </Badge>
        <Badge variant="outline" class="flex items-center gap-1 text-[11px] py-1">
          <Smartphone class="w-3.5 h-3.5 text-emerald-500" /> Mobile Touch Guard
        </Badge>
        <Badge variant="outline" class="flex items-center gap-1 text-[11px] py-1">
          <FileCode class="w-3.5 h-3.5 text-violet-500" /> SVG & Biometric
        </Badge>
      </div>
    </div>

    <!-- Main Workspace Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- Left Column: Interactive Signature Board (7 cols) -->
      <div class="lg:col-span-7 space-y-5">
        <Card class="border-border/80 shadow-xs overflow-hidden">
          <CardHeader class="pb-3 border-b border-border/50 bg-slate-50/50 dark:bg-slate-900/50">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <CardTitle class="text-base font-semibold flex items-center gap-2">
                  <Activity class="w-4 h-4 text-primary" />
                  กระดานทดสอบเซ็นชื่อ (Live Interactive Pad)
                </CardTitle>
                <CardDescription class="text-xs">
                  ทดสอบด้วยเมาส์บน Desktop, นิ้วมือบน Mobile, หรือปากกาบน iPad/Tablet
                </CardDescription>
              </div>

              <!-- Color Palette -->
              <div class="flex items-center gap-1 bg-white dark:bg-slate-950 p-1 rounded-lg border border-border/70">
                <button
                  v-for="color in colorPresets"
                  :key="color.value"
                  type="button"
                  @click="penColor = color.value"
                  :title="color.name"
                  class="w-5 h-5 rounded-full transition-transform"
                  :class="[
                    color.class,
                    penColor === color.value ? 'scale-110 ring-2 ring-offset-2 ring-primary' : 'opacity-80 hover:opacity-100'
                  ]"
                ></button>
              </div>
            </div>
          </CardHeader>

          <CardContent class="pt-4 space-y-4">
            <!-- Pen Stroke Thickness Controls -->
            <div class="flex flex-wrap items-center justify-between gap-3 text-xs bg-slate-50 dark:bg-slate-900/40 p-2.5 rounded-lg border border-border/60">
              <div class="flex items-center gap-2">
                <span class="text-muted-foreground font-medium">ความหนาของเส้น:</span>
                <div class="inline-flex rounded-md shadow-2xs">
                  <button
                    type="button"
                    @click="strokePreset = 'thin'"
                    class="px-2.5 py-1 text-xs font-medium rounded-l-md border border-border transition-colors"
                    :class="strokePreset === 'thin' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-muted'"
                  >
                    บาง (0.8 - 2px)
                  </button>
                  <button
                    type="button"
                    @click="strokePreset = 'normal'"
                    class="px-2.5 py-1 text-xs font-medium border-t border-b border-border transition-colors"
                    :class="strokePreset === 'normal' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-muted'"
                  >
                    ปานกลาง (1.5 - 3.5px)
                  </button>
                  <button
                    type="button"
                    @click="strokePreset = 'thick'"
                    class="px-2.5 py-1 text-xs font-medium rounded-r-md border border-border transition-colors"
                    :class="strokePreset === 'thick' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-muted'"
                  >
                    หนา (2.5 - 5.5px)
                  </button>
                </div>
              </div>

              <!-- Disabled toggle for testing -->
              <label class="flex items-center gap-1.5 cursor-pointer text-muted-foreground hover:text-foreground">
                <input
                  type="checkbox"
                  v-model="isDisabled"
                  class="rounded border-border text-primary focus:ring-primary w-3.5 h-3.5"
                />
                <span>ล็อกกระดาน (Disabled)</span>
              </label>
            </div>

            <!-- Canvas Component -->
            <SignaturePadCanvas
              ref="padRef"
              :pen-color="penColor"
              :min-width="minMaxWidth.min"
              :max-width="minMaxWidth.max"
              :disabled="isDisabled"
              @stroke-end="handleStrokeEnd"
            />

            <!-- Export Buttons -->
            <div class="pt-2 border-t border-border/60 flex flex-wrap items-center justify-between gap-2">
              <span class="text-xs text-muted-foreground font-medium">ส่งออกไฟล์ (Export Formats):</span>
              <div class="flex flex-wrap items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  @click="handleDownloadPng"
                  class="h-8 text-xs flex items-center gap-1.5"
                >
                  <Download class="w-3.5 h-3.5" /> PNG โปร่งใส
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  @click="handleDownloadJpeg"
                  class="h-8 text-xs flex items-center gap-1.5"
                >
                  <Download class="w-3.5 h-3.5" /> JPEG พื้นขาว
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  @click="handleDownloadSvg"
                  class="h-8 text-xs flex items-center gap-1.5 text-primary border-primary/30 hover:bg-primary/5"
                >
                  <FileCode class="w-3.5 h-3.5" /> SVG Vector
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Simulated Patient Consent Form Box (Inertia useForm simulator) -->
        <Card class="border-border/80 shadow-xs">
          <CardHeader class="pb-3">
            <CardTitle class="text-base flex items-center gap-2">
              <FileText class="w-4 h-4 text-emerald-600" />
              จำลองส่งแบบฟอร์มยินยอมการรักษา (Consent Form with Inertia.js)
            </CardTitle>
            <CardDescription class="text-xs">
              ทดสอบการรวบรวมลายเซ็นเพื่อส่งข้อมูลเข้าสู่ Laravel Backend API ผ่าน Inertia Form
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="text-xs text-muted-foreground leading-relaxed bg-slate-50 dark:bg-slate-900/60 p-3 rounded-lg border border-border/50">
              <p class="font-semibold text-foreground mb-1">ข้อกำหนดการรักษาและยินยอมเปิดเผยข้อมูล (PDPA):</p>
              ข้าพเจ้ายินยอมให้คลินิกดำเนินการตรวจวินิจฉัยและรักษาตามมาตรฐานวิชาชีพเวชกรรม และยินยอมให้จัดเก็บข้อมูลสุขภาพและลายเซ็นอิเล็กทรอนิกส์นี้เพื่อประกอบเวชระเบียนผู้ป่วย
            </div>

            <div class="flex items-center justify-between">
              <div class="text-xs text-muted-foreground">
                สถานะลายเซ็น:
                <span
                  class="font-medium inline-flex items-center gap-1 ml-1"
                  :class="signatureDataUrl ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-500'"
                >
                  <CheckCircle2 v-if="signatureDataUrl" class="w-3.5 h-3.5" />
                  {{ signatureDataUrl ? 'ลงลายเซ็นเรียบร้อย' : 'รอการลงลายเซ็น' }}
                </span>
              </div>

              <Button
                @click="handleMockInertiaSubmit"
                :disabled="isSubmitting || !signatureDataUrl"
                class="bg-blue-600 hover:bg-blue-700 text-white text-xs h-9 px-4 flex items-center gap-2"
              >
                <Sparkles v-if="!isSubmitting" class="w-3.5 h-3.5" />
                <span v-if="isSubmitting">กำลังประมวลผล...</span>
                <span v-else>จำลองการส่งข้อมูล (form.post)</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Right Column: Audit Trail & Device Inspection (5 cols) -->
      <div class="lg:col-span-5 space-y-5">
        <!-- Live Signature Preview Card -->
        <Card class="border-border/80 shadow-xs">
          <CardHeader class="pb-3">
            <CardTitle class="text-sm font-semibold flex items-center gap-2">
              <ShieldCheck class="w-4 h-4 text-emerald-500" />
              ภาพพรีวิวลายเซ็นจริง (Real-time Captured Image)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div class="h-36 w-full rounded-lg border border-dashed border-border bg-slate-100/50 dark:bg-slate-900/50 flex items-center justify-center overflow-hidden p-2">
              <img
                v-if="signatureDataUrl"
                :src="signatureDataUrl"
                alt="Signature Preview"
                class="max-h-full max-w-full object-contain filter drop-shadow-xs"
              />
              <span v-else class="text-xs text-muted-foreground/60">
                ยังไม่มีข้อมูลลายเซ็น (เริ่มเซ็นในกรอบเพื่อดูพรีวิว)
              </span>
            </div>
          </CardContent>
        </Card>

        <!-- Audit & Biometric Point Inspector -->
        <Card class="border-border/80 shadow-xs">
          <CardHeader class="pb-3">
            <CardTitle class="text-sm font-semibold flex items-center gap-2">
              <Layers class="w-4 h-4 text-violet-500" />
              ข้อมูลพยานหลักฐานและนิติเวชศาสตร์ (Audit & Biometrics)
            </CardTitle>
            <CardDescription class="text-xs">
              `signature_pad` เก็บข้อมูลพิกัด (X, Y), แรงกด (Pressure), และเวลา (Timestamp) ของทุกจุด
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-3">
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-border/50">
                <span class="text-muted-foreground block text-[11px]">จำนวนเส้นที่ลาก (Strokes):</span>
                <span class="text-base font-bold font-mono text-foreground">{{ pointGroupsCount }} เส้น</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-border/50">
                <span class="text-muted-foreground block text-[11px]">จำนวนจุดพิกัด (Points):</span>
                <span class="text-base font-bold font-mono text-foreground">{{ totalPointsCount }} จุด</span>
              </div>
            </div>

            <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-border/50 text-xs space-y-1.5">
              <div class="flex justify-between">
                <span class="text-muted-foreground">เวลาที่บันทึกข้อมูลล่าสุด:</span>
                <span class="font-mono font-medium text-foreground">{{ lastTimestamp || '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">เทคโนโลยีการดักจับ:</span>
                <span class="font-medium text-emerald-600 dark:text-emerald-400">W3C PointerEvents (Native)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">ความแม่นยำจอ Retina:</span>
                <span class="font-medium text-blue-600 dark:text-blue-400">DevicePixelRatio x{{ currentDpr }}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Hardware & Platform Checklist -->
        <Card class="border-border/80 shadow-xs bg-slate-50/50 dark:bg-slate-900/30">
          <CardHeader class="pb-2">
            <CardTitle class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Info class="w-3.5 h-3.5" />
              การรองรับอุปกรณ์ในคลินิก
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-2 text-xs">
            <div class="flex items-start gap-2">
              <Monitor class="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
              <div>
                <span class="font-medium text-foreground">Desktop (เคาน์เตอร์ / แพทย์):</span>
                <p class="text-muted-foreground text-[11px]">ใช้เมาส์หรือ Trackpad ลากเส้นเรียบเนียน มี Bézier Curve ป้องกันเส้นหักเหลี่ยม</p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <Tablet class="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
              <div>
                <span class="font-medium text-foreground">Tablet (iPad / Galaxy Tab จุดลงทะเบียน):</span>
                <p class="text-muted-foreground text-[11px]">รองรับ Apple Pencil / S-Pen ตรวจจับแรงกดจริงได้ มี Palm Rejection ระดับฮาร์ดแวร์</p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <Smartphone class="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <span class="font-medium text-foreground">Mobile (มือถือคนไข้):</span>
                <p class="text-muted-foreground text-[11px]">ใส่ `touch-action: none` ล็อกหน้าจอไม่ให้เด้งเลื่อนขึ้น-ลงขณะใช้นิ้วเซ็น</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
