<script setup lang="ts">
import { computed, ref } from 'vue';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { toast } from 'vue-sonner';
import { CheckCircle2, CreditCard, FileText, Printer, QrCode } from '@lucide/vue';
import type { Appointment } from './mockData';
import { clinicBranches } from './mockData';

const props = defineProps<{
    open: boolean;
    appointment: Appointment | null;
}>();

const emit = defineEmits<{
    (e: 'update:open', value: boolean): void;
    (e: 'paid', appointmentId: string): void;
}>();

const paymentMethod = ref<'promptpay' | 'card' | 'cash'>('promptpay');
const isProcessing = ref(false);

const branch = computed(() => {
    if (!props.appointment) return null;
    return clinicBranches.find((b) => b.id === props.appointment?.branchId);
});

const invoiceNumber = computed(() => {
    if (!props.appointment) return '';
    return `INV-2026-${props.appointment.id.replace('apt-', '')}`;
});

function handlePay() {
    if (!props.appointment) return;
    isProcessing.value = true;

    setTimeout(() => {
        isProcessing.value = false;
        toast.success(`ออกใบเสร็จรับเงินสำเร็จ (${invoiceNumber.value})`, {
            description: `ชำระเงินเรียบร้อยสำหรับคุณ ${props.appointment?.patientName} ยอดสุทธิ ฿${props.appointment?.price.toLocaleString()}`
        });
        emit('paid', props.appointment.id);
        emit('update:open', false);
    }, 600);
}

function handleMockPrint() {
    toast.info('ระบบกำลังพิมพ์เอกสารใบแจ้งหนี้ (Mock Print)...');
}
</script>

<template>
    <Dialog :open="open" @update:open="(val) => emit('update:open', val)">
        <DialogContent class="sm:max-w-[550px]">
            <DialogHeader>
                <div class="flex items-center justify-between pr-6">
                    <DialogTitle class="flex items-center gap-2 text-xl font-bold">
                        <FileText class="size-5 text-primary" />
                        ออกบิลค่ารักษาพยาบาล (Mock Billing)
                    </DialogTitle>
                    <Badge variant="outline" class="font-mono text-xs">
                        {{ invoiceNumber }}
                    </Badge>
                </div>
                <DialogDescription>
                    ตรวจสอบข้อมูลการรักษาและดำเนินการชำระเงินสำหรับคนไข้
                </DialogDescription>
            </DialogHeader>

            <div v-if="appointment" class="space-y-4 py-2">
                <!-- Patient & Clinic Meta -->
                <div class="grid grid-cols-2 gap-3 rounded-lg border bg-muted/40 p-3 text-sm">
                    <div>
                        <span class="text-xs text-muted-foreground">ชื่อคนไข้:</span>
                        <div class="font-semibold text-foreground">
                            {{ appointment.patientName }}
                        </div>
                        <div class="text-xs text-muted-foreground">
                            โทร: {{ appointment.patientPhone }}
                        </div>
                    </div>
                    <div>
                        <span class="text-xs text-muted-foreground">สาขาที่เข้ารับบริการ:</span>
                        <div class="font-medium text-foreground">
                            {{ branch?.name }}
                        </div>
                        <div class="text-xs text-muted-foreground">
                            แพทย์: {{ appointment.doctorName }}
                        </div>
                    </div>
                </div>

                <!-- Treatment Bill Items Table -->
                <div class="rounded-lg border overflow-hidden">
                    <table class="w-full text-left text-sm">
                        <thead class="bg-muted/60 text-xs uppercase text-muted-foreground">
                            <tr>
                                <th class="px-3 py-2">รายการรักษา</th>
                                <th class="px-3 py-2 text-center">จำนวน</th>
                                <th class="px-3 py-2 text-right">ราคา (บาท)</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y">
                            <tr>
                                <td class="px-3 py-2 font-medium">
                                    {{ appointment.treatment }}
                                </td>
                                <td class="px-3 py-2 text-center">1</td>
                                <td class="px-3 py-2 text-right font-mono font-medium">
                                    {{ appointment.price.toLocaleString() }}
                                </td>
                            </tr>
                        </tbody>
                        <tfoot class="bg-muted/20 border-t font-semibold">
                            <tr>
                                <td colspan="2" class="px-3 py-2 text-right text-xs">
                                    ยอดรวมสุทธิ (Total Amount):
                                </td>
                                <td class="px-3 py-2 text-right font-mono text-base text-primary">
                                    ฿{{ appointment.price.toLocaleString() }}
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>

                <!-- Payment Method Selection -->
                <div class="space-y-2">
                    <span class="text-xs font-semibold text-muted-foreground">
                        เลือกช่องทางการชำระเงิน:
                    </span>
                    <div class="grid grid-cols-3 gap-2">
                        <button
                            type="button"
                            @click="paymentMethod = 'promptpay'"
                            :class="[
                                'flex items-center justify-center gap-1.5 p-2 rounded-md border text-xs font-medium transition-all',
                                paymentMethod === 'promptpay'
                                    ? 'border-primary bg-primary/10 text-primary font-semibold'
                                    : 'border-border bg-background hover:bg-muted'
                            ]"
                        >
                            <QrCode class="size-4" />
                            พร้อมเพย์ QR
                        </button>
                        <button
                            type="button"
                            @click="paymentMethod = 'card'"
                            :class="[
                                'flex items-center justify-center gap-1.5 p-2 rounded-md border text-xs font-medium transition-all',
                                paymentMethod === 'card'
                                    ? 'border-primary bg-primary/10 text-primary font-semibold'
                                    : 'border-border bg-background hover:bg-muted'
                            ]"
                        >
                            <CreditCard class="size-4" />
                            บัตรเครดิต
                        </button>
                        <button
                            type="button"
                            @click="paymentMethod = 'cash'"
                            :class="[
                                'flex items-center justify-center gap-1.5 p-2 rounded-md border text-xs font-medium transition-all',
                                paymentMethod === 'cash'
                                    ? 'border-primary bg-primary/10 text-primary font-semibold'
                                    : 'border-border bg-background hover:bg-muted'
                            ]"
                        >
                            <CheckCircle2 class="size-4" />
                            เงินสด
                        </button>
                    </div>
                </div>

                <div v-if="appointment.status === 'paid'" class="rounded-md bg-emerald-50 p-2.5 text-center text-xs font-medium text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400">
                    ✅ นัดหมายนี้ชำระเงินเรียบร้อยแล้ว
                </div>
            </div>

            <DialogFooter class="flex sm:justify-between gap-2">
                <Button variant="outline" size="sm" @click="handleMockPrint" class="gap-1.5">
                    <Printer class="size-4" />
                    พิมพ์ใบแจ้งหนี้
                </Button>
                <div class="flex gap-2">
                    <Button variant="ghost" size="sm" @click="emit('update:open', false)">
                        ปิด
                    </Button>
                    <Button
                        size="sm"
                        class="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold gap-1.5"
                        :disabled="isProcessing || appointment?.status === 'paid'"
                        @click="handlePay"
                    >
                        <CheckCircle2 class="size-4" />
                        {{ isProcessing ? 'กำลังบันทึก...' : 'บันทึกรับชำระเงิน' }}
                    </Button>
                </div>
            </DialogFooter>
        </DialogContent>
    </Dialog>
</template>
