<script setup lang="ts">
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Edit3,
    CreditCard,
    Clock,
    Phone,
    MapPin,
    Stethoscope,
    Users,
    CheckCircle2,
    Calendar,
} from '@lucide/vue';
import type { Appointment } from '../mockData';
import { clinicBranches } from '../mockData';

const props = defineProps<{
    open: boolean;
    appointments: Appointment[];
    timeSlot?: string;
}>();

const emit = defineEmits<{
    (e: 'update:open', val: boolean): void;
    (e: 'edit', apt: Appointment): void;
    (e: 'bill', apt: Appointment): void;
}>();

function getBranch(branchId: string) {
    return clinicBranches.find((b) => b.id === branchId);
}

function getInitials(name: string): string {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
}

function formatTime(dateVal: string | undefined): string {
    if (!dateVal) return '';
    const d = new Date(dateVal);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleTimeString('th-TH', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
    });
}
</script>

<template>
    <Dialog :open="open" @update:open="(val) => emit('update:open', val)">
        <DialogContent class="sm:max-w-[650px] p-0 overflow-hidden border-border/80 shadow-lg">
            <!-- Modal Header -->
            <div class="bg-muted/40 p-5 border-b border-border/60">
                <DialogHeader>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">
                            <Users class="size-3.5" />
                            <span>{{ appointments.length }} นัดหมายเวลาเดียวกัน</span>
                        </span>
                        <span v-if="timeSlot" class="inline-flex items-center gap-1 text-xs text-muted-foreground font-mono">
                            <Clock class="size-3" />
                            <span>{{ timeSlot }}</span>
                        </span>
                    </div>
                    <DialogTitle class="text-lg font-bold text-foreground">
                        จัดการนัดหมายที่ซ้อนทับกัน (Concurrent Appointments)
                    </DialogTitle>
                    <DialogDescription class="text-xs text-muted-foreground">
                        มีแพทย์และคนไข้เข้ารับบริการในเวลาเดียวกัน คุณสามารถดูข้อมูล ออกบิล หรือแก้ไขเวลานัดหมายได้เป็นรายเคส
                    </DialogDescription>
                </DialogHeader>
            </div>

            <!-- List of Concurrent Appointments (Rich Cards) -->
            <div class="p-5 space-y-3.5 max-h-[65vh] overflow-y-auto">
                <article
                    v-for="(apt, index) in appointments"
                    :key="apt.id"
                    class="rounded-lg border border-border/80 bg-card p-3.5 shadow-xs transition-all hover:border-primary/50 hover:shadow-sm"
                    :style="{
                        borderLeftWidth: '5px',
                        borderLeftColor: getBranch(apt.branchId)?.color || '#3b82f6',
                    }"
                >
                    <!-- Card Top: Patient Info & Status Badge -->
                    <div class="flex items-start justify-between gap-2">
                        <div class="flex items-center gap-3">
                            <div
                                class="size-10 rounded-full font-bold text-xs flex items-center justify-center shrink-0 border"
                                :class="
                                    apt.status === 'paid'
                                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800'
                                        : 'bg-primary/10 text-primary border-primary/20'
                                "
                            >
                                {{ getInitials(apt.patientName) }}
                            </div>
                            <div>
                                <div class="flex items-center gap-2">
                                    <h4 class="font-bold text-sm text-foreground">
                                        {{ apt.patientName }}
                                    </h4>
                                    <Badge
                                        :variant="apt.status === 'paid' ? 'outline' : 'secondary'"
                                        class="text-[10px] px-1.5 py-0 h-4 font-medium"
                                        :class="
                                            apt.status === 'paid'
                                                ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5'
                                                : 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300'
                                        "
                                    >
                                        {{ apt.status === 'paid' ? 'ชำระแล้ว' : 'รอออกบิล' }}
                                    </Badge>
                                </div>
                                <div class="text-xs text-muted-foreground font-mono flex items-center gap-1 mt-0.5">
                                    <Phone class="size-3 text-muted-foreground/70" />
                                    <span>{{ apt.patientPhone }}</span>
                                </div>
                            </div>
                        </div>

                        <!-- Price Tag -->
                        <div class="text-right shrink-0">
                            <div class="font-mono text-base font-bold text-foreground">
                                ฿{{ apt.price?.toLocaleString() }}
                            </div>
                            <div class="text-[10px] text-muted-foreground">ค่ารักษา</div>
                        </div>
                    </div>

                    <!-- Card Middle: Treatment & Doctor Info -->
                    <div class="mt-3 grid grid-cols-1 gap-1.5 sm:grid-cols-2 rounded-md bg-muted/30 p-2 text-xs">
                        <div class="flex items-center gap-1.5 text-foreground/90">
                            <Stethoscope class="size-3.5 text-primary shrink-0" />
                            <span class="font-medium truncate">{{ apt.treatment }}</span>
                        </div>
                        <div class="flex items-center gap-1.5 text-muted-foreground">
                            <span class="font-medium">👨‍⚕️ {{ apt.doctorName }}</span>
                        </div>
                        <div class="flex items-center gap-1.5 text-muted-foreground">
                            <MapPin class="size-3.5 text-muted-foreground/70 shrink-0" />
                            <span class="truncate">{{ getBranch(apt.branchId)?.name.split(' (')[0] }}</span>
                        </div>
                        <div class="flex items-center gap-1.5 text-muted-foreground font-mono">
                            <Clock class="size-3.5 text-muted-foreground/70 shrink-0" />
                            <span>{{ formatTime(apt.start) }} - {{ formatTime(apt.end) }} น.</span>
                        </div>
                    </div>

                    <p v-if="apt.notes" class="mt-2 text-[11px] text-muted-foreground italic pl-1 border-l-2 border-border">
                        "{{ apt.notes }}"
                    </p>

                    <!-- Card Actions -->
                    <div class="mt-3 flex items-center justify-end gap-2 border-t border-border/40 pt-2.5">
                        <Button
                            size="sm"
                            variant="outline"
                            class="h-7 px-2.5 text-xs gap-1 border-border shadow-2xs hover:bg-muted cursor-pointer"
                            @click="emit('edit', apt)"
                        >
                            <Edit3 class="size-3 text-muted-foreground" />
                            <span>แก้ไขนัดหมาย</span>
                        </Button>

                        <Button
                            size="sm"
                            :variant="apt.status === 'paid' ? 'outline' : 'default'"
                            class="h-7 px-3 text-xs font-semibold gap-1.5 shadow-2xs cursor-pointer"
                            :class="
                                apt.status === 'paid'
                                    ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400'
                                    : ''
                            "
                            @click="emit('bill', apt)"
                        >
                            <CreditCard class="size-3" />
                            <span>{{ apt.status === 'paid' ? 'ดูบิล' : 'ออกบิลค่ารักษา' }}</span>
                        </Button>
                    </div>
                </article>
            </div>

            <!-- Modal Footer -->
            <div class="bg-muted/30 px-5 py-3 border-t border-border/60 flex items-center justify-between text-xs text-muted-foreground">
                <span class="flex items-center gap-1">
                    <CheckCircle2 class="size-3.5 text-emerald-500" />
                    <span>ข้อมูลเชื่อมโยงกับฐานข้อมูลคลินิกและระบบบิลแบบเรียลไทม์</span>
                </span>
                <Button size="sm" variant="ghost" class="cursor-pointer" @click="emit('update:open', false)">
                    ปิดหน้าต่าง
                </Button>
            </div>
        </DialogContent>
    </Dialog>
</template>
