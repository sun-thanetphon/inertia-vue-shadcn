<script setup lang="ts">
import { computed, ref } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import VueCal from 'vue-cal';
import 'vue-cal/dist/vuecal.css';
import 'vue-cal/dist/drag-and-drop.es.js';

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { toast } from 'vue-sonner';
import {
    ArrowLeft,
    Building2,
    CalendarDays,
    CheckCircle2,
    ChevronLeft,
    ChevronRight,
    Clock,
    Coins,
    Columns3,
    CreditCard,
    Edit3,
    Filter,
    MapPin,
    Move,
    Plus,
    Search,
    Sparkles,
    Stethoscope,
    Users,
} from '@lucide/vue';

import type { Appointment } from '../mockData';
import { clinicBranches, clinicDoctors, getInitialAppointments } from '../mockData';
import BillingDialog from '../BillingDialog.vue';
import AppointmentFormDialog from '../AppointmentFormDialog.vue';

// 1. Reactive State
const appointments = ref<Appointment[]>(getInitialAppointments());
const selectedBranchId = ref<string>('all'); // 'all' | 'b1' | 'b2' | 'b3'
const selectedDoctorId = ref<string>('all'); // 'all' | doctorName
const searchQuery = ref<string>('');
const isSplitViewMode = ref<boolean>(true); // Split days toggle
const activeView = ref<'week' | 'day' | 'month'>('week');
const vueCalRef = ref<any>(null);

// Dialogs state
const isBillingOpen = ref(false);
const selectedBillingAppointment = ref<Appointment | null>(null);

const isFormOpen = ref(false);
const editingAppointment = ref<Appointment | null>(null);
const formInitialDate = ref<string>('');

// Format helper: Convert ISO "2026-09-11T09:00:00" to "2026-09-11 09:00" for Vue-Cal
function toVueCalDate(isoStr: string): string {
    return isoStr.replace('T', ' ').slice(0, 16);
}

// Safe time formatter for Date objects, extended Vue-Cal dates, or ISO strings
function formatTime(val: any): string {
    if (!val) return '';
    if (typeof val === 'string') {
        if (val.includes(' ') || val.includes('T')) {
            const timePart = val.includes('T') ? val.split('T')[1] : val.split(' ')[1];
            return timePart.slice(0, 5);
        }
        return val.slice(0, 5);
    }
    if (val instanceof Date) {
        const hours = String(val.getHours()).padStart(2, '0');
        const mins = String(val.getMinutes()).padStart(2, '0');
        return `${hours}:${mins}`;
    }
    if (typeof val?.format === 'function') {
        return val.format('HH:mm');
    }
    return '';
}

// 2. Vue-Cal Split Days Configuration (3 Branches Side-by-Side)
const splitDays = [
    {
        id: 1,
        branchKey: 'b1',
        label: 'สยามสแควร์',
        sublabel: 'ชั้น 4 สยามสแควร์วัน',
        class: 'split-siam',
        color: '#3b82f6',
    },
    {
        id: 2,
        branchKey: 'b2',
        label: 'อารีย์',
        sublabel: 'อาคารลาวิลล่า',
        class: 'split-ari',
        color: '#10b981',
    },
    {
        id: 3,
        branchKey: 'b3',
        label: 'ทองหล่อ',
        sublabel: 'ทองหล่อ ซอย 10',
        class: 'split-thonglo',
        color: '#8b5cf6',
    },
];

function getSplitNumber(branchId: string): number {
    if (branchId === 'b1') return 1;
    if (branchId === 'b2') return 2;
    return 3;
}

// 3. Multi-dimensional Filtering
const filteredAppointments = computed(() => {
    return appointments.value.filter((apt) => {
        // Filter by Branch
        if (selectedBranchId.value !== 'all' && apt.branchId !== selectedBranchId.value) {
            return false;
        }
        // Filter by Doctor
        if (selectedDoctorId.value !== 'all' && apt.doctorName !== selectedDoctorId.value) {
            return false;
        }
        // Filter by Search (Name or Phone)
        if (searchQuery.value.trim()) {
            const query = searchQuery.value.toLowerCase().trim();
            const matchName = apt.patientName.toLowerCase().includes(query);
            const matchPhone = apt.patientPhone.includes(query);
            const matchTreatment = apt.treatment.toLowerCase().includes(query);
            if (!matchName && !matchPhone && !matchTreatment) return false;
        }
        return true;
    });
});

// Map appointments to Vue-Cal Event format with rich attributes
const vueCalEvents = computed(() => {
    return filteredAppointments.value.map((apt) => {
        const branch = clinicBranches.find((b) => b.id === apt.branchId);
        return {
            id: apt.id,
            title: apt.title,
            start: toVueCalDate(apt.start),
            end: toVueCalDate(apt.end),
            split: getSplitNumber(apt.branchId),
            class: apt.status === 'paid' ? 'event-paid' : `event-${apt.branchId}`,
            // Custom extended props
            patientName: apt.patientName,
            patientPhone: apt.patientPhone,
            doctorName: apt.doctorName,
            branchName: branch?.name.split(' (')[0] || '',
            branchColor: branch?.color || '#3b82f6',
            branchId: apt.branchId,
            treatment: apt.treatment,
            price: apt.price,
            status: apt.status,
            notes: apt.notes,
        };
    });
});

// 4. Live Operational Metrics (Restrained Product Strip)
const stats = computed(() => {
    const total = appointments.value.length;
    const pending = appointments.value.filter((a) => a.status === 'pending_bill');
    const paid = appointments.value.filter((a) => a.status === 'paid');
    const totalPendingAmount = pending.reduce((sum, a) => sum + a.price, 0);
    const totalCollectedAmount = paid.reduce((sum, a) => sum + a.price, 0);

    return {
        total,
        pendingCount: pending.length,
        pendingAmount: totalPendingAmount,
        paidCount: paid.length,
        paidAmount: totalCollectedAmount,
        activeDoctors: clinicDoctors.length,
    };
});

function getBranchAppointmentCount(branchKey: string): number {
    return appointments.value.filter((a) => a.branchId === branchKey).length;
}

// 5. Drag & Drop Handlers
function onEventChange(eventData: any) {
    const targetEvent = eventData.event || eventData;
    const apt = appointments.value.find((a) => a.id === targetEvent.id);

    if (apt && targetEvent) {
        if (targetEvent.start) {
            const startStr = typeof targetEvent.start === 'string'
                ? targetEvent.start
                : targetEvent.start.format('YYYY-MM-DD HH:mm');
            apt.start = `${startStr.replace(' ', 'T')}:00`;
        }
        if (targetEvent.end) {
            const endStr = typeof targetEvent.end === 'string'
                ? targetEvent.end
                : targetEvent.end.format('YYYY-MM-DD HH:mm');
            apt.end = `${endStr.replace(' ', 'T')}:00`;
        }

        // Branch transfer across splits
        if (targetEvent.split) {
            const newBranchKey = splitDays.find((s) => s.id === targetEvent.split)?.branchKey;
            if (newBranchKey && (newBranchKey === 'b1' || newBranchKey === 'b2' || newBranchKey === 'b3')) {
                apt.branchId = newBranchKey;
            }
        }

        const branch = clinicBranches.find((b) => b.id === apt.branchId);
        const timeDisplay = formatTime(apt.start);

        toast.success('ย้ายเวลานัดหมายสำเร็จ', {
            description: `${apt.patientName} เวลา ${timeDisplay} น. (${branch?.name.split(' (')[0]})`
        });
    }
}

// 6. Navigation Controls for Vue-Cal
function previousPeriod() {
    vueCalRef.value?.previous();
}

function nextPeriod() {
    vueCalRef.value?.next();
}

function goToToday() {
    vueCalRef.value?.switchView(activeView.value, new Date());
}

// 7. Actions & Modal Handlers
function handleOpenBilling(event: any) {
    const apt = appointments.value.find((a) => a.id === event.id);
    if (apt) {
        selectedBillingAppointment.value = apt;
        isBillingOpen.value = true;
    }
}

function handleCellClick(date: Date) {
    formInitialDate.value = date.toISOString().split('T')[0];
    editingAppointment.value = null;
    isFormOpen.value = true;
}

function handleEditAppointment(event: any) {
    const apt = appointments.value.find((a) => a.id === event.id);
    if (apt) {
        editingAppointment.value = apt;
        isFormOpen.value = true;
    }
}

function handleSaveAppointment(newApt: Appointment) {
    const index = appointments.value.findIndex((a) => a.id === newApt.id);
    if (index >= 0) {
        appointments.value[index] = newApt;
    } else {
        appointments.value.push(newApt);
    }
}

function handleMarkAsPaid(appointmentId: string) {
    const apt = appointments.value.find((a) => a.id === appointmentId);
    if (apt) {
        apt.status = 'paid';
    }
}
</script>

<template>
    <Head title="ตารางนัดหมายคลินิก - Vue-Cal Scheduler" />

    <div class="flex-1 space-y-3.5 p-4 md:p-5 max-w-[1720px] mx-auto min-h-screen flex flex-col justify-start">
        <!-- 1. Header Bar: Title + Context + Actions -->
        <header class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b pb-3">
            <div class="flex items-center gap-2.5">
                <div class="size-8 rounded-lg bg-emerald-600/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
                    <CalendarDays class="size-4.5" />
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-lg font-bold tracking-tight text-foreground">
                            ตารางนัดหมายคลินิก
                        </h1>
                        <span class="text-xs font-semibold px-2 py-0.5 rounded bg-muted text-muted-foreground">
                            Vue-Cal Engine
                        </span>
                    </div>
                    <p class="text-xs text-muted-foreground">
                        จัดการคิวและนัดหมายคนไข้พร้อมกัน 3 สาขา ด้วยระบบเสาคู่ขนาน (Split Columns)
                    </p>
                </div>
            </div>

            <!-- Top Actions -->
            <div class="flex items-center gap-2 self-stretch sm:self-auto">
                <Link href="/poc/fullcalendar">
                    <Button variant="ghost" size="sm" class="h-8 text-xs text-muted-foreground hover:text-foreground gap-1.5">
                        <ArrowLeft class="size-3.5" />
                        <span>สลับไป FullCalendar</span>
                    </Button>
                </Link>

                <Button
                    size="sm"
                    class="h-8 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold gap-1.5 px-3 shadow-xs"
                    @click="() => { editingAppointment = null; formInitialDate = ''; isFormOpen = true; }"
                >
                    <Plus class="size-3.5" />
                    <span>เพิ่มนัดหมาย</span>
                </Button>
            </div>
        </header>

        <!-- 2. High-Density Operational Pulse Strip (Restrained, Space-Saving) -->
        <section aria-label="Operational Pulse" class="flex flex-wrap items-center justify-between gap-2 px-3.5 py-2 rounded-lg border bg-card/60 text-xs font-medium">
            <div class="flex flex-wrap items-center gap-4 sm:gap-6 divide-x divide-border">
                <!-- Total Appointments -->
                <div class="flex items-center gap-2">
                    <span class="size-2 rounded-full bg-blue-500" />
                    <span class="text-muted-foreground">นัดหมายทั้งหมด:</span>
                    <span class="font-bold text-foreground font-mono">{{ stats.total }} เคส</span>
                </div>

                <!-- Pending Billing -->
                <div class="flex items-center gap-2 pl-4 sm:pl-6">
                    <span class="size-2 rounded-full bg-amber-500 animate-pulse" />
                    <span class="text-muted-foreground">รอออกบิล:</span>
                    <span class="font-bold text-amber-600 dark:text-amber-400 font-mono">
                        {{ stats.pendingCount }} เคส
                    </span>
                    <span class="text-[11px] text-muted-foreground font-mono">
                        (฿{{ stats.pendingAmount.toLocaleString() }})
                    </span>
                </div>

                <!-- Completed & Paid -->
                <div class="flex items-center gap-2 pl-4 sm:pl-6">
                    <span class="size-2 rounded-full bg-emerald-500" />
                    <span class="text-muted-foreground">ชำระแล้ว:</span>
                    <span class="font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                        {{ stats.paidCount }} เคส
                    </span>
                    <span class="text-[11px] text-muted-foreground font-mono">
                        (฿{{ stats.paidAmount.toLocaleString() }})
                    </span>
                </div>

                <!-- Active Doctors -->
                <div class="hidden md:flex items-center gap-2 pl-4 sm:pl-6">
                    <Stethoscope class="size-3.5 text-purple-500" />
                    <span class="text-muted-foreground">แพทย์เข้าเวร:</span>
                    <span class="font-bold text-foreground font-mono">{{ stats.activeDoctors }} ท่าน</span>
                </div>
            </div>

            <!-- Branch Status Dots Indicator -->
            <div class="hidden lg:flex items-center gap-3 text-[11px] text-muted-foreground">
                <span class="flex items-center gap-1">
                    <span class="size-1.5 rounded-full bg-blue-500" /> สยาม ({{ getBranchAppointmentCount('b1') }})
                </span>
                <span class="flex items-center gap-1">
                    <span class="size-1.5 rounded-full bg-emerald-500" /> อารีย์ ({{ getBranchAppointmentCount('b2') }})
                </span>
                <span class="flex items-center gap-1">
                    <span class="size-1.5 rounded-full bg-purple-500" /> ทองหล่อ ({{ getBranchAppointmentCount('b3') }})
                </span>
            </div>
        </section>

        <!-- 3. Unified Ergonomic Control Toolbar (Date Navigation + Filters + View Controls) -->
        <nav aria-label="Calendar Navigation and Filters" class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2.5 p-2 rounded-lg border bg-card">
            <!-- Left: Date Navigator -->
            <div class="flex items-center gap-1.5">
                <div class="flex items-center border rounded-md overflow-hidden bg-background">
                    <button
                        type="button"
                        @click="previousPeriod"
                        class="p-1.5 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors border-r"
                        title="ช่วงก่อนหน้า"
                    >
                        <ChevronLeft class="size-4" />
                    </button>
                    <button
                        type="button"
                        @click="goToToday"
                        class="px-2.5 py-1 text-xs font-semibold hover:bg-muted text-foreground transition-colors"
                    >
                        วันนี้
                    </button>
                    <button
                        type="button"
                        @click="nextPeriod"
                        class="p-1.5 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors border-l"
                        title="ช่วงถัดไป"
                    >
                        <ChevronRight class="size-4" />
                    </button>
                </div>
            </div>

            <!-- Center: Filters (Branch, Doctor, Live Search) -->
            <div class="flex flex-wrap items-center gap-2">
                <!-- Branch Filter -->
                <Select v-model="selectedBranchId">
                    <SelectTrigger class="w-[170px] h-8 text-xs bg-background">
                        <SelectValue placeholder="กรองสาขา" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">
                            🏢 ทุกสาขา
                        </SelectItem>
                        <SelectItem
                            v-for="b in clinicBranches"
                            :key="b.id"
                            :value="b.id"
                        >
                            <div class="flex items-center gap-2">
                                <span class="size-2 rounded-full" :style="{ backgroundColor: b.color }" />
                                <span>{{ b.name.split(' (')[0] }}</span>
                            </div>
                        </SelectItem>
                    </SelectContent>
                </Select>

                <!-- Doctor Filter -->
                <Select v-model="selectedDoctorId">
                    <SelectTrigger class="w-[165px] h-8 text-xs bg-background">
                        <SelectValue placeholder="แพทย์ทุกคน" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">
                            👨‍⚕️ แพทย์ทุกคน
                        </SelectItem>
                        <SelectItem
                            v-for="d in clinicDoctors"
                            :key="d.id"
                            :value="d.name"
                        >
                            {{ d.name }}
                        </SelectItem>
                    </SelectContent>
                </Select>

                <!-- Live Search Box -->
                <div class="relative w-[180px]">
                    <Search class="size-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                    <Input
                        v-model="searchQuery"
                        placeholder="ค้นหาคนไข้..."
                        class="h-8 pl-8 text-xs bg-background"
                    />
                </div>
            </div>

            <!-- Right: View Modes & Split Switcher -->
            <div class="flex items-center gap-1.5">
                <!-- Split Days Toggle -->
                <button
                    type="button"
                    @click="isSplitViewMode = !isSplitViewMode"
                    class="h-8 px-2.5 rounded-md border text-xs font-semibold flex items-center gap-1.5 transition-colors"
                    :class="isSplitViewMode
                        ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-700 dark:text-emerald-300'
                        : 'bg-background border-border text-muted-foreground hover:bg-muted'"
                    title="สลับโหมดเสาสาขาคู่ขนาน"
                >
                    <Columns3 class="size-3.5" />
                    <span>{{ isSplitViewMode ? 'เสาสาขา (Split)' : 'คอลัมน์รวม' }}</span>
                </button>
            </div>
        </nav>

        <!-- 4. The Master Vue-Cal Calendar Canvas -->
        <main class="flex-1 rounded-lg border bg-card overflow-hidden shadow-xs vuecal-clinic-master-wrapper">
            <vue-cal
                ref="vueCalRef"
                class="vuecal--clinic-theme"
                :active-view="activeView"
                :disable-views="['years', 'year']"
                :time-from="8 * 60"
                :time-to="20 * 60"
                :time-step="30"
                :time-cell-height="66"
                :events="vueCalEvents"
                :split-days="isSplitViewMode && selectedBranchId === 'all' ? splitDays : []"
                :sticky-split-labels="true"
                :editable-events="{ title: false, drag: true, resize: true, delete: false, create: false }"
                :drag-to-create-event="false"
                @event-change="onEventChange"
                @event-drop="onEventChange"
                @cell-click="handleCellClick"
            >
                <!-- 🎯 Split Column Header Slot -->
                <template #split-label="{ split }">
                    <div class="flex items-center justify-between px-2.5 py-1.5 border-b border-border/80 bg-muted/40 text-left">
                        <div class="flex items-center gap-1.5 min-w-0">
                            <span
                                class="size-2 rounded-full shrink-0"
                                :style="{ backgroundColor: split.color }"
                            />
                            <div class="min-w-0">
                                <div class="font-bold text-xs text-foreground truncate">
                                    {{ split.label }}
                                </div>
                                <div class="text-[10px] text-muted-foreground truncate">
                                    {{ split.sublabel }}
                                </div>
                            </div>
                        </div>
                        <span class="text-[10px] font-mono font-semibold px-1.5 py-0.2 rounded bg-background border text-muted-foreground shrink-0">
                            {{ getBranchAppointmentCount(split.branchKey) }}
                        </span>
                    </div>
                </template>

                <!-- 🎯 Custom Event Card Slot: Designed with High Information Density & Zero Noise -->
                <template #event="{ event }">
                    <article
                        class="group relative flex flex-col justify-between w-full h-full p-2 rounded-md text-left overflow-hidden select-none cursor-pointer transition-all border"
                        :class="[
                            event.status === 'paid'
                                ? 'bg-emerald-500/10 text-emerald-950 dark:text-emerald-100 border-emerald-500/30'
                                : 'bg-card text-foreground border-border hover:border-emerald-500/50 shadow-xs'
                        ]"
                        @click="handleEditAppointment(event)"
                    >
                        <!-- Header Row: Patient Name & Status -->
                        <div class="space-y-1">
                            <div class="flex items-center justify-between gap-1">
                                <!-- Patient Name with Initial Tag -->
                                <div class="flex items-center gap-1.5 min-w-0">
                                    <span
                                        class="size-4.5 rounded text-[9px] font-black flex items-center justify-center shrink-0 leading-none"
                                        :class="event.status === 'paid' ? 'bg-emerald-600 text-white' : 'bg-primary/10 text-primary'"
                                    >
                                        {{ event.patientName?.slice(0, 1) }}
                                    </span>
                                    <span class="font-bold text-xs truncate leading-tight">
                                        {{ event.patientName }}
                                    </span>
                                </div>

                                <!-- Semantic Status Dot / Tag -->
                                <span
                                    class="text-[9px] font-semibold px-1.5 py-0.2 rounded shrink-0 flex items-center gap-1"
                                    :class="event.status === 'paid'
                                        ? 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300'
                                        : 'bg-amber-500/15 text-amber-700 dark:text-amber-400'"
                                >
                                    <span
                                        class="size-1.5 rounded-full"
                                        :class="event.status === 'paid' ? 'bg-emerald-600' : 'bg-amber-500 animate-pulse'"
                                    />
                                    <span>{{ event.status === 'paid' ? 'ชำระแล้ว' : 'รอออกบิล' }}</span>
                                </span>
                            </div>

                            <!-- Treatment & Doctor -->
                            <div class="text-[11px] font-semibold truncate leading-tight" :class="event.status === 'paid' ? 'text-emerald-800 dark:text-emerald-200' : 'text-foreground'">
                                {{ event.title }}
                            </div>

                            <div class="flex items-center justify-between text-[10px] text-muted-foreground leading-tight">
                                <span class="truncate">👨‍⚕️ {{ event.doctorName?.split(' ')[1] }}</span>
                                <span class="font-mono text-[9px] font-bold text-muted-foreground shrink-0">
                                    {{ formatTime(event.start) }} - {{ formatTime(event.end) }}
                                </span>
                            </div>
                        </div>

                        <!-- Footer Row: Price & Actions -->
                        <div class="flex items-center justify-between gap-1 pt-1 mt-1 border-t border-border/50">
                            <span class="font-mono font-bold text-[11px] text-foreground tracking-tight">
                                ฿{{ event.price?.toLocaleString() }}
                            </span>

                            <div class="flex items-center gap-1">
                                <!-- Quick Edit Button -->
                                <button
                                    type="button"
                                    @click.stop="handleEditAppointment(event)"
                                    class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                                    title="แก้ไขเวลานัดหมาย"
                                >
                                    <Edit3 class="size-3" />
                                </button>

                                <!-- 💳 Billing Button (ออกบิล) -->
                                <button
                                    type="button"
                                    @click.stop="handleOpenBilling(event)"
                                    class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold transition-all shadow-xs"
                                    :class="event.status === 'paid'
                                        ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                                        : 'bg-amber-500 hover:bg-amber-600 text-white'"
                                    title="คลิกเพื่อจัดการบิลค่ารักษา"
                                >
                                    <CreditCard class="size-3" />
                                    <span>{{ event.status === 'paid' ? 'ดูบิล' : 'ออกบิล' }}</span>
                                </button>
                            </div>
                        </div>
                    </article>
                </template>
            </vue-cal>
        </main>

        <!-- 5. Quiet Ergonomic Assist Footer -->
        <footer class="flex flex-wrap items-center justify-between gap-3 text-[11px] text-muted-foreground px-2">
            <div class="flex items-center gap-4">
                <span class="flex items-center gap-1">
                    <Move class="size-3 text-emerald-600" />
                    <span>ลากกล่องเพื่อเลื่อนเวลาหรือย้ายสาขา</span>
                </span>
                <span class="flex items-center gap-1">
                    <Plus class="size-3 text-emerald-600" />
                    <span>คลิกช่องว่างเพื่อเพิ่มนัดหมาย</span>
                </span>
                <span class="flex items-center gap-1">
                    <CreditCard class="size-3 text-emerald-600" />
                    <span>คลิกออกบิลเพื่อตัดชำระเงิน</span>
                </span>
            </div>
            <span class="font-mono text-[10px]">
                Active Appointments: {{ filteredAppointments.length }} of {{ appointments.length }}
            </span>
        </footer>

        <!-- Modals -->
        <BillingDialog
            v-model:open="isBillingOpen"
            :appointment="selectedBillingAppointment"
            @paid="handleMarkAsPaid"
        />

        <AppointmentFormDialog
            v-model:open="isFormOpen"
            :initial-date="formInitialDate"
            :initial-branch-id="selectedBranchId === 'all' ? 'b1' : (selectedBranchId as 'b1' | 'b2' | 'b3')"
            :editing-appointment="editingAppointment"
            @save="handleSaveAppointment"
        />
    </div>
</template>

<style>
/* Vue-Cal Clinic Master Theme - Ultra Clean & Seamless Theme Sync */
.vuecal-clinic-master-wrapper .vuecal {
    height: calc(100vh - 250px);
    min-height: 680px;
    background-color: var(--card, #ffffff);
    color: var(--foreground, #0f172a);
    border: none;
    font-family: inherit;
}

.vuecal-clinic-master-wrapper .vuecal__menu,
.vuecal-clinic-master-wrapper .vuecal__view-selector {
    display: none; /* Handled by our unified external toolbar */
}

.vuecal-clinic-master-wrapper .vuecal__title-bar {
    background-color: var(--muted, #f8fafc);
    border-bottom: 1px solid var(--border, #e2e8f0);
    font-weight: 700;
    font-size: 0.85rem;
    min-height: 36px;
}

.vuecal-clinic-master-wrapper .vuecal__today-btn {
    display: none;
}

/* Time column gutter */
.vuecal-clinic-master-wrapper .vuecal__time-cell-line {
    border-top: 1px solid var(--border, #e2e8f0);
    opacity: 0.5;
}

.vuecal-clinic-master-wrapper .vuecal__time-column {
    font-size: 0.725rem;
    font-weight: 600;
    font-family: monospace;
    color: var(--muted-foreground, #64748b);
    border-right: 1px solid var(--border, #e2e8f0);
}

/* Event Box General Overrides */
.vuecal-clinic-master-wrapper .vuecal__event {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 1.5px !important;
}

/* Split Column Tinting */
.vuecal-clinic-master-wrapper .split-siam {
    background-color: rgba(59, 130, 246, 0.015);
}

.vuecal-clinic-master-wrapper .split-ari {
    background-color: rgba(16, 185, 129, 0.015);
}

.vuecal-clinic-master-wrapper .split-thonglo {
    background-color: rgba(139, 92, 246, 0.015);
}

/* Day Heading */
.vuecal-clinic-master-wrapper .vuecal__weekdays-headings {
    border-bottom: 1px solid var(--border, #e2e8f0);
}

.vuecal-clinic-master-wrapper .vuecal__heading {
    font-weight: 700;
    font-size: 0.8rem;
    padding: 6px 0;
}
</style>
