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
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'vue-sonner';
import {
    ArrowLeft,
    Building2,
    CalendarDays,
    CheckCircle2,
    Clock,
    Coins,
    Columns3,
    CreditCard,
    Edit3,
    Filter,
    MapPin,
    Move,
    Phone,
    Plus,
    Search,
    Sparkles,
    Stethoscope,
    User,
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
        sublabel: 'สยามสแควร์วัน ชั้น 4',
        class: 'split-siam',
        color: '#3b82f6',
        accentBg: 'bg-blue-500/10 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800'
    },
    {
        id: 2,
        branchKey: 'b2',
        label: 'สาขา อารีย์',
        sublabel: 'ลาวิลล่า พหลโยธิน',
        class: 'split-ari',
        color: '#10b981',
        accentBg: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
    },
    {
        id: 3,
        branchKey: 'b3',
        label: 'สาขา ทองหล่อ',
        sublabel: 'ทองหล่อ ซอย 10',
        class: 'split-thonglo',
        color: '#8b5cf6',
        accentBg: 'bg-purple-500/10 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800'
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

// 4. Live Statistics Cards Calculation
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

// Count per split branch
function getBranchAppointmentCount(branchKey: string): number {
    return appointments.value.filter((a) => a.branchId === branchKey).length;
}

// 5. Drag & Drop and Event Change Handlers
function onEventChange(eventData: any) {
    const targetEvent = eventData.event || eventData;
    const apt = appointments.value.find((a) => a.id === targetEvent.id);

    if (apt && targetEvent) {
        // Update times
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

        // Check if dragged to another split column
        if (targetEvent.split) {
            const newBranchKey = splitDays.find((s) => s.id === targetEvent.split)?.branchKey;
            if (newBranchKey && (newBranchKey === 'b1' || newBranchKey === 'b2' || newBranchKey === 'b3')) {
                apt.branchId = newBranchKey;
            }
        }

        const branch = clinicBranches.find((b) => b.id === apt.branchId);
        const timeDisplay = formatTime(apt.start);

        toast.success('ย้ายเวลานัดหมายสำเร็จ (Drag & Drop)', {
            description: `${apt.patientName}: เวลาใหม่ ${timeDisplay} น. (${branch?.name.split(' (')[0]})`
        });
    }
}

// 6. Actions & Modal Handlers
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
    <Head title="PoC Vue-Cal - Clinic Appointment Master" />

    <div class="flex-1 space-y-5 p-4 md:p-6 max-w-[1700px] mx-auto">
        <!-- Top Navigation & Header Banner -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-b pb-4">
            <div class="flex items-center gap-3">
                <div class="flex size-11 items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 text-white shadow-md shadow-emerald-500/20">
                    <CalendarDays class="size-6" />
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-2xl font-black tracking-tight text-foreground">
                            ระบบตารางนัดหมายคลินิก (Vue-Cal Engine)
                        </h1>
                        <Badge class="bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 text-xs font-bold gap-1 px-2.5 py-0.5">
                            <Sparkles class="size-3" />
                            Ultra Customizable
                        </Badge>
                    </div>
                    <p class="text-xs md:text-sm text-muted-foreground mt-0.5">
                        ระบบจัดการคิวนัดหมายหลายสาขาคู่ขนาน (Split Columns), ย้ายวันเวลาด้วย Drag & Drop, และออกบิลค่ารักษาแบบ Real-time
                    </p>
                </div>
            </div>

            <!-- Action Controls -->
            <div class="flex items-center gap-2.5">
                <Link href="/poc/fullcalendar">
                    <Button variant="outline" size="sm" class="gap-1.5 border-border hover:bg-muted text-xs">
                        <ArrowLeft class="size-3.5" />
                        <span>เปรียบเทียบกับ FullCalendar</span>
                    </Button>
                </Link>

                <Button
                    size="sm"
                    class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold gap-1.5 shadow-sm shadow-emerald-600/30 px-3.5"
                    @click="() => { editingAppointment = null; formInitialDate = ''; isFormOpen = true; }"
                >
                    <Plus class="size-4" />
                    เพิ่มนัดหมายใหม่
                </Button>
            </div>
        </div>

        <!-- 📊 Live Clinic Metrics Summary Bar -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <!-- Metric 1: Total Appointments -->
            <Card class="border shadow-xs bg-card/80 backdrop-blur-xs">
                <CardContent class="p-3.5 flex items-center justify-between">
                    <div>
                        <span class="text-xs font-semibold text-muted-foreground">นัดหมายทั้งหมด</span>
                        <div class="text-2xl font-black text-foreground mt-0.5">
                            {{ stats.total }} <span class="text-xs font-normal text-muted-foreground">เคส</span>
                        </div>
                        <div class="flex items-center gap-1.5 text-[11px] text-muted-foreground mt-1">
                            <Building2 class="size-3 text-emerald-500" />
                            <span>ครอบคลุม 3 สาขา</span>
                        </div>
                    </div>
                    <div class="size-10 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center">
                        <Users class="size-5" />
                    </div>
                </CardContent>
            </Card>

            <!-- Metric 2: Pending Billing -->
            <Card class="border shadow-xs bg-card/80 backdrop-blur-xs">
                <CardContent class="p-3.5 flex items-center justify-between">
                    <div>
                        <span class="text-xs font-semibold text-amber-600 dark:text-amber-400">รอออกบิล / ชำระ</span>
                        <div class="text-2xl font-black text-amber-600 dark:text-amber-400 mt-0.5">
                            {{ stats.pendingCount }} <span class="text-xs font-normal text-muted-foreground">เคส</span>
                        </div>
                        <div class="flex items-center gap-1 text-[11px] font-mono text-amber-600/90 dark:text-amber-400/90 mt-1">
                            <span>ยอดรวม ฿{{ stats.pendingAmount.toLocaleString() }}</span>
                        </div>
                    </div>
                    <div class="size-10 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center">
                        <Clock class="size-5" />
                    </div>
                </CardContent>
            </Card>

            <!-- Metric 3: Paid & Completed -->
            <Card class="border shadow-xs bg-card/80 backdrop-blur-xs">
                <CardContent class="p-3.5 flex items-center justify-between">
                    <div>
                        <span class="text-xs font-semibold text-emerald-600 dark:text-emerald-400">ชำระเงินเรียบร้อย</span>
                        <div class="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-0.5">
                            {{ stats.paidCount }} <span class="text-xs font-normal text-muted-foreground">เคส</span>
                        </div>
                        <div class="flex items-center gap-1 text-[11px] font-mono text-emerald-600/90 dark:text-emerald-400/90 mt-1">
                            <span>รับแล้ว ฿{{ stats.paidAmount.toLocaleString() }}</span>
                        </div>
                    </div>
                    <div class="size-10 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                        <Coins class="size-5" />
                    </div>
                </CardContent>
            </Card>

            <!-- Metric 4: Duty Doctors -->
            <Card class="border shadow-xs bg-card/80 backdrop-blur-xs">
                <CardContent class="p-3.5 flex items-center justify-between">
                    <div>
                        <span class="text-xs font-semibold text-muted-foreground">แพทย์ผู้ตรวจ</span>
                        <div class="text-2xl font-black text-foreground mt-0.5">
                            {{ stats.activeDoctors }} <span class="text-xs font-normal text-muted-foreground">ท่าน</span>
                        </div>
                        <div class="flex items-center gap-1.5 text-[11px] text-muted-foreground mt-1">
                            <Stethoscope class="size-3 text-purple-500" />
                            <span>พร้อมปฏิบัติการตรวจ</span>
                        </div>
                    </div>
                    <div class="size-10 rounded-lg bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center">
                        <Stethoscope class="size-5" />
                    </div>
                </CardContent>
            </Card>
        </div>

        <!-- 🎛️ Advanced Interactive Filter & View Bar -->
        <Card class="shadow-xs border bg-card/90">
            <CardContent class="p-3.5 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
                <!-- Left: Branch, Doctor, and Search Filters -->
                <div class="flex flex-wrap items-center gap-2.5">
                    <!-- Branch Filter -->
                    <div class="flex items-center gap-1.5">
                        <Filter class="size-4 text-emerald-600" />
                        <span class="text-xs font-semibold text-muted-foreground">สาขา:</span>
                    </div>
                    <Select v-model="selectedBranchId">
                        <SelectTrigger class="w-[200px] h-9 text-xs font-medium">
                            <SelectValue placeholder="เลือกสาขา" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">
                                🏢 ทั้งหมด (ทุกสาขา)
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
                    <div class="flex items-center gap-1.5 ml-1">
                        <Stethoscope class="size-4 text-purple-600" />
                        <span class="text-xs font-semibold text-muted-foreground">แพทย์:</span>
                    </div>
                    <Select v-model="selectedDoctorId">
                        <SelectTrigger class="w-[190px] h-9 text-xs font-medium">
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

                    <!-- Search Input -->
                    <div class="relative w-[210px]">
                        <Search class="size-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            v-model="searchQuery"
                            placeholder="ค้นคนไข้ / เบอร์โทร..."
                            class="h-9 pl-8 pr-2 text-xs"
                        />
                    </div>
                </div>

                <!-- Right: Split Mode Toggle & View Selector -->
                <div class="flex items-center gap-2">
                    <!-- Toggle Split Columns Mode -->
                    <Button
                        variant="outline"
                        size="sm"
                        @click="isSplitViewMode = !isSplitViewMode"
                        class="h-9 gap-1.5 text-xs font-semibold transition-all"
                        :class="isSplitViewMode
                            ? 'border-emerald-500 bg-emerald-50 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-700'
                            : 'border-border text-muted-foreground'"
                    >
                        <Columns3 class="size-4 text-emerald-600" />
                        <span>{{ isSplitViewMode ? 'เสาสาขาคู่ขนาน (Split On)' : 'คอลัมน์รวมปกติ' }}</span>
                    </Button>
                </div>
            </CardContent>
        </Card>

        <!-- 📅 Vue-Cal Master Calendar Container -->
        <Card class="shadow-sm border overflow-hidden">
            <CardContent class="p-3 md:p-5 vuecal-clinic-master-wrapper">
                <vue-cal
                    class="vuecal--clinic-theme"
                    :active-view="activeView"
                    :disable-views="['years', 'year']"
                    :time-from="8 * 60"
                    :time-to="20 * 60"
                    :time-step="30"
                    :time-cell-height="68"
                    :events="vueCalEvents"
                    :split-days="isSplitViewMode && selectedBranchId === 'all' ? splitDays : []"
                    :sticky-split-labels="true"
                    :editable-events="{ title: false, drag: true, resize: true, delete: false, create: false }"
                    :drag-to-create-event="false"
                    @event-change="onEventChange"
                    @event-drop="onEventChange"
                    @cell-click="handleCellClick"
                >
                    <!-- 🎯 Split Header Custom Slot (สาขาและจำนวนเคส) -->
                    <template #split-label="{ split }">
                        <div class="flex items-center justify-between px-3 py-2 border-b border-border/80 bg-muted/40">
                            <div class="flex items-center gap-2">
                                <span
                                    class="size-2.5 rounded-full shadow-xs"
                                    :style="{ backgroundColor: split.color }"
                                />
                                <div class="text-left">
                                    <div class="font-bold text-xs text-foreground tracking-tight">
                                        {{ split.label }}
                                    </div>
                                    <div class="text-[10px] text-muted-foreground flex items-center gap-0.5">
                                        <MapPin class="size-2.5" />
                                        <span>{{ split.sublabel }}</span>
                                    </div>
                                </div>
                            </div>
                            <Badge variant="outline" class="text-[10px] font-mono font-bold bg-background/90 px-1.5 py-0">
                                {{ getBranchAppointmentCount(split.branchKey) }} เคส
                            </Badge>
                        </div>
                    </template>

                    <!-- 🎯 Custom Event Card Slot: รายละเอียดคนไข้ + ปุ่มออกบิล + เวลา -->
                    <template #event="{ event }">
                        <div
                            class="group relative flex flex-col justify-between w-full h-full p-2 rounded-lg text-left overflow-hidden select-none cursor-pointer transition-all duration-200 hover:shadow-md border"
                            :class="[
                                event.status === 'paid'
                                    ? 'bg-emerald-950/90 text-white border-emerald-500/40 shadow-emerald-900/20'
                                    : 'bg-card text-foreground border-border/90 shadow-xs hover:border-primary/50'
                            ]"
                            @click="handleEditAppointment(event)"
                        >
                            <!-- Top Accent Line -->
                            <div
                                class="absolute top-0 left-0 right-0 h-1"
                                :style="{ backgroundColor: event.status === 'paid' ? '#10b981' : event.branchColor }"
                            />

                            <!-- Patient Info Header -->
                            <div class="space-y-1 pt-0.5">
                                <div class="flex items-center justify-between gap-1">
                                    <!-- Patient Name -->
                                    <div class="flex items-center gap-1.5 min-w-0">
                                        <div
                                            class="size-5 rounded-full flex items-center justify-center text-[9px] font-black shrink-0"
                                            :class="event.status === 'paid' ? 'bg-emerald-800 text-emerald-100' : 'bg-primary/10 text-primary'"
                                        >
                                            {{ event.patientName?.slice(0, 2) }}
                                        </div>
                                        <span class="font-bold text-xs truncate leading-tight">
                                            {{ event.patientName }}
                                        </span>
                                    </div>

                                    <!-- Status Pill -->
                                    <span
                                        class="text-[9px] font-bold px-1.5 py-0.2 rounded-full shrink-0 flex items-center gap-0.5"
                                        :class="event.status === 'paid'
                                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                            : 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30'"
                                    >
                                        <CheckCircle2 v-if="event.status === 'paid'" class="size-2.5" />
                                        <Clock v-else class="size-2.5" />
                                        {{ event.status === 'paid' ? 'ชำระแล้ว' : 'รอออกบิล' }}
                                    </span>
                                </div>

                                <!-- Treatment Title -->
                                <div class="text-[11px] font-semibold truncate" :class="event.status === 'paid' ? 'text-emerald-100' : 'text-primary'">
                                    {{ event.title }}
                                </div>

                                <!-- Doctor & Time -->
                                <div class="flex items-center justify-between text-[10px] text-muted-foreground" :class="event.status === 'paid' ? 'text-emerald-200/80' : ''">
                                    <div class="flex items-center gap-1 truncate">
                                        <Stethoscope class="size-3 text-purple-500 shrink-0" />
                                        <span class="truncate">{{ event.doctorName?.split(' ')[1] }}</span>
                                    </div>
                                    <span class="font-mono text-[9px] font-bold">
                                        {{ formatTime(event.start) }} - {{ formatTime(event.end) }}
                                    </span>
                                </div>
                            </div>

                            <!-- Bottom Action Row: Price Tag & ออกบิล Button -->
                            <div class="flex items-center justify-between gap-1.5 mt-1.5 pt-1.5 border-t border-border/50">
                                <!-- Treatment Price -->
                                <span class="font-mono font-bold text-[11px] tracking-tight" :class="event.status === 'paid' ? 'text-emerald-300' : 'text-foreground'">
                                    ฿{{ event.price?.toLocaleString() }}
                                </span>

                                <!-- Action Buttons -->
                                <div class="flex items-center gap-1">
                                    <!-- Edit Trigger Button -->
                                    <button
                                        type="button"
                                        @click.stop="handleEditAppointment(event)"
                                        class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted/80 transition-colors"
                                        title="แก้ไขเวลานัดหมาย"
                                    >
                                        <Edit3 class="size-3" />
                                    </button>

                                    <!-- 💳 Billing Button (ออกบิล) -->
                                    <button
                                        type="button"
                                        @click.stop="handleOpenBilling(event)"
                                        class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold shadow-xs transition-transform active:scale-95"
                                        :class="event.status === 'paid'
                                            ? 'bg-emerald-700/80 hover:bg-emerald-700 text-white'
                                            : 'bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white shadow-amber-500/20'"
                                        title="คลิกเพื่อออกบิลค่ารักษา"
                                    >
                                        <CreditCard class="size-3" />
                                        <span>{{ event.status === 'paid' ? 'ดูใบเสร็จ' : 'ออกบิล' }}</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </template>
                </vue-cal>
            </CardContent>
        </Card>

        <!-- 🌟 Feature Capabilities & Architecture Ledger -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
            <div class="p-3 rounded-xl border bg-card/60 flex items-start gap-2.5">
                <Columns3 class="size-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold text-foreground">1. เสาสาขาคู่ขนาน (Split Days):</span>
                    <p class="text-muted-foreground mt-0.5 leading-relaxed">
                        แสดง 3 สาขาข้างกันแบบเรียลไทม์ และสามารถลากกล่องนัดหมายข้ามเสาเพื่อเปลี่ยนสาขาได้ทันที
                    </p>
                </div>
            </div>

            <div class="p-3 rounded-xl border bg-card/60 flex items-start gap-2.5">
                <Filter class="size-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold text-foreground">2. กรองข้อมูลหลายมิติ:</span>
                    <p class="text-muted-foreground mt-0.5 leading-relaxed">
                        กรองได้ทั้งตามสาขา, กรองตามแพทย์ผู้ตรวจ หรือค้นหาชื่อและเบอร์โทรคนไข้
                    </p>
                </div>
            </div>

            <div class="p-3 rounded-xl border bg-card/60 flex items-start gap-2.5">
                <Move class="size-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold text-foreground">3. Drag & Drop เต็มรูปแบบ:</span>
                    <p class="text-muted-foreground mt-0.5 leading-relaxed">
                        ลากเพื่อเลื่อนเวลา และยืดหดขอบล่างของกล่องเพื่อเพิ่ม/ลดระยะเวลาการรักษา
                    </p>
                </div>
            </div>

            <div class="p-3 rounded-xl border bg-card/60 flex items-start gap-2.5">
                <CreditCard class="size-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold text-foreground">4. ออกบิลค่ารักษา (Billing):</span>
                    <p class="text-muted-foreground mt-0.5 leading-relaxed">
                        คลิกปุ่มออกบิลเพื่อเปิดใบเสร็จรับเงิน พร้อมระบบบันทึกสถานะชำระเงินลงปฏิทินทันที
                    </p>
                </div>
            </div>
        </div>

        <!-- Shared Modals -->
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
    height: 780px;
    background-color: var(--card, #ffffff);
    color: var(--foreground, #0f172a);
    border-radius: 0.75rem;
    border: 1px solid var(--border, #e2e8f0);
    font-family: inherit;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.vuecal-clinic-master-wrapper .vuecal__menu,
.vuecal-clinic-master-wrapper .vuecal__view-selector {
    background-color: var(--muted, #f8fafc);
    border-bottom: 1px solid var(--border, #e2e8f0);
}

.vuecal-clinic-master-wrapper .vuecal__view-btn {
    border-radius: 0.375rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--muted-foreground, #64748b);
    transition: all 0.15s ease;
}

.vuecal-clinic-master-wrapper .vuecal__view-btn:hover {
    color: var(--foreground, #0f172a);
}

.vuecal-clinic-master-wrapper .vuecal__view-btn--active {
    background-color: #059669 !important;
    color: #ffffff !important;
    box-shadow: 0 1px 3px rgba(5, 150, 105, 0.25);
}

.vuecal-clinic-master-wrapper .vuecal__title-bar {
    background-color: var(--muted, #f8fafc);
    border-bottom: 1px solid var(--border, #e2e8f0);
    font-weight: 700;
}

.vuecal-clinic-master-wrapper .vuecal__today-btn {
    font-size: 0.8rem;
    font-weight: 600;
    border-radius: 0.375rem;
    border: 1px solid var(--border, #e2e8f0);
    background-color: var(--card, #ffffff);
    color: var(--foreground, #0f172a);
}

/* Time column gutter */
.vuecal-clinic-master-wrapper .vuecal__time-cell-line {
    border-top: 1px dashed var(--border, #e2e8f0);
    opacity: 0.6;
}

.vuecal-clinic-master-wrapper .vuecal__time-column {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--muted-foreground, #64748b);
    border-right: 1px solid var(--border, #e2e8f0);
}

/* Event Box General Overrides */
.vuecal-clinic-master-wrapper .vuecal__event {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 1px !important;
}

/* Split Column Tinting */
.vuecal-clinic-master-wrapper .split-siam {
    background-color: rgba(59, 130, 246, 0.02);
}

.vuecal-clinic-master-wrapper .split-ari {
    background-color: rgba(16, 185, 129, 0.02);
}

.vuecal-clinic-master-wrapper .split-thonglo {
    background-color: rgba(139, 92, 246, 0.02);
}

/* Day Heading */
.vuecal-clinic-master-wrapper .vuecal__weekdays-headings {
    border-bottom: 1px solid var(--border, #e2e8f0);
}

.vuecal-clinic-master-wrapper .vuecal__heading {
    font-weight: 700;
    font-size: 0.85rem;
}
</style>
