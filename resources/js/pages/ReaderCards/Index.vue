<script setup lang="ts">
import { Head, router } from "@inertiajs/vue3";
import { useAsyncState } from "@vueuse/core";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { LoaderCircle, IdCard, User, ShieldAlert } from "lucide-vue-next";

// รับ props เพิ่มเติม ทั้ง cardData และ error จาก Controller
const props = defineProps<{
    cardData?: any;
    error?: string;
}>();

const { execute, isLoading } = useAsyncState(
    async () => {
        return new Promise((resolve) => {
            router.get(
                "/readers/1",
                {},
                {
                    preserveScroll: true,
                    onFinish: () => resolve(true),
                },
            );
        });
    },
    null,
    { immediate: false },
);

defineOptions({
    layout: {
        breadcrumbs: [
            {
                title: "Demo",
                href: "/reader",
            },
        ],
    },
});
</script>

<template>
    <Head title="Reader Card Dashboard" />

    <div class="flex h-full flex-1 flex-col gap-6 p-6">
        <div
            class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
        >
            <div>
                <h1 class="text-2xl font-bold tracking-tight">
                    ระบบอ่านบัตรประชาชน
                </h1>
                <p class="text-sm text-muted-foreground">
                    จัดการและดึงข้อมูลจากเครื่องอ่านสมาร์ทคาร์ด
                </p>
            </div>

            <Button
                @click="execute()"
                :disabled="isLoading"
                size="lg"
                class="shadow-sm"
            >
                <LoaderCircle
                    v-if="isLoading"
                    class="mr-2 h-5 w-5 animate-spin"
                />
                <IdCard v-else class="mr-2 h-5 w-5" />
                <span>{{
                    isLoading ? "กำลังอ่านข้อมูล..." : "อ่านข้อมูลบัตร"
                }}</span>
            </Button>
        </div>

        <!-- แจ้งเตือนกรณีเกิดข้อผิดพลาด เช่น ไม่ได้เสียบบัตร -->
        <Card
            v-if="props.error && !isLoading"
            class="border-destructive/50 bg-destructive/10 text-destructive"
        >
            <CardContent class="flex items-center gap-3 py-4">
                <ShieldAlert class="h-5 w-5 flex-shrink-0" />
                <div>
                    <h4 class="font-semibold text-sm">
                        ไม่สามารถอ่านข้อมูลบัตรได้
                    </h4>
                    <p class="text-xs opacity-90 mt-0.5">{{ props.error }}</p>
                </div>
            </CardContent>
        </Card>

        <Card v-if="isLoading" class="border-dashed">
            <CardContent
                class="flex flex-col items-center justify-center py-16 text-center"
            >
                <LoaderCircle
                    class="h-10 w-10 animate-spin text-primary mb-4"
                />
                <h3 class="font-semibold text-lg">กำลังประมวลผลข้อมูล</h3>
                <p class="text-sm text-muted-foreground max-w-sm mt-1">
                    กรุณารอสักครู่ ระบบกำลังดึงข้อมูลจริงจากเครื่องอ่านบัตรผ่าน
                    Spring Boot...
                </p>
            </CardContent>
        </Card>

        <Card v-else-if="props.cardData" class="shadow-sm">
            <CardHeader class="border-b bg-muted/40 pb-4">
                <div class="flex items-center justify-between">
                    <div>
                        <CardTitle class="text-lg flex items-center gap-2">
                            <IdCard class="h-5 w-5 text-primary" />
                            ข้อมูลบัตรประจำตัวประชาชน
                        </CardTitle>
                        <CardDescription
                            >รายละเอียดข้อมูลที่อ่านได้จากชิปการ์ด</CardDescription
                        >
                    </div>
                    <span
                        class="inline-flex items-center rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20 dark:bg-green-950/30 dark:text-green-400"
                    >
                        สถานะ: ปกติ
                    </span>
                </div>
            </CardHeader>
            <CardContent class="grid gap-6 pt-6 sm:grid-cols-2 lg:grid-cols-3">
                <div class="space-y-1">
                    <span
                        class="text-xs font-medium text-muted-foreground uppercase tracking-wider"
                        >เลขประจำตัวประชาชน</span
                    >
                    <p class="text-base font-semibold">
                        {{ props.cardData.national_id }}
                    </p>
                </div>

                <div class="space-y-1">
                    <span
                        class="text-xs font-medium text-muted-foreground uppercase tracking-wider"
                        >ชื่อ-นามสกุล (ภาษาไทย)</span
                    >
                    <p class="text-base font-semibold">
                        {{ props.cardData.prefix_th }}
                        {{ props.cardData.firstname_th }}
                        {{ props.cardData.lastname_th }}
                    </p>
                </div>

                <div class="space-y-1">
                    <span
                        class="text-xs font-medium text-muted-foreground uppercase tracking-wider"
                        >ชื่อ-นามสกุล (ภาษาอังกฤษ)</span
                    >
                    <p class="text-base font-semibold">
                        {{ props.cardData.prefix_en }}
                        {{ props.cardData.firstname_en }}
                        {{ props.cardData.lastname_en }}
                    </p>
                </div>

                <!-- วันเกิด & เพศ -->
                <div class="space-y-1">
                    <span
                        class="text-xs font-medium text-muted-foreground uppercase tracking-wider"
                        >วันเกิด / เพศ</span
                    >
                    <p class="text-base font-semibold">
                        {{ props.cardData.birth_date }} ({{
                            props.cardData.gender
                        }})
                    </p>
                </div>

                <div class="space-y-1">
                    <span
                        class="text-xs font-medium text-muted-foreground uppercase tracking-wider"
                        >วันออกบัตร / วันหมดอายุ</span
                    >
                    <p class="text-base font-semibold">
                        {{ props.cardData.issue_date }} ถึง
                        {{ props.cardData.expire_date }}
                    </p>
                </div>

                <div class="space-y-1">
                    <span
                        class="text-xs font-medium text-muted-foreground uppercase tracking-wider"
                        >Chip ID</span
                    >
                    <p class="text-base font-mono text-muted-foreground">
                        {{ props.cardData.chip_id }}
                    </p>
                </div>

                <div
                    class="space-y-1 sm:col-span-2 lg:col-span-3 border-t pt-4"
                >
                    <span
                        class="text-xs font-medium text-muted-foreground uppercase tracking-wider"
                        >ที่อยู่ตามภูมิลำเนา</span
                    >
                    <p class="text-base font-medium text-foreground/90">
                        {{ props.cardData.address }}
                    </p>
                </div>
            </CardContent>
        </Card>

        <Card v-else-if="!props.error" class="border-dashed bg-card/50">
            <CardContent
                class="flex flex-col items-center justify-center py-20 text-center"
            >
                <div
                    class="rounded-full bg-muted p-4 mb-3 text-muted-foreground"
                >
                    <User class="h-8 w-8" />
                </div>
                <h3 class="font-semibold text-lg">ยังไม่มีข้อมูลการอ่านบัตร</h3>
                <p class="text-sm text-muted-foreground max-w-sm mt-1">
                    กรุณาเสียบบัตรเข้าเครื่องอ่าน และกดปุ่ม
                    <span class="font-medium text-foreground"
                        >"อ่านข้อมูลบัตร"</span
                    >
                    ด้านบนเพื่อเริ่มต้น
                </p>
            </CardContent>
        </Card>
    </div>
</template>
