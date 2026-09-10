<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import PlaceholderPattern from "@/components/PlaceholderPattern.vue";
import { dashboard } from "@/routes";
import { Button } from "@/components/ui/button";

// const page = usePage();
// const permissions = page.props.auth.permissions as string[];

// const can = (permission: string) => {
//     return permissions.includes(permission);
// };

defineOptions({
    layout: {
        breadcrumbs: [
            {
                title: "Dashboard",
                href: dashboard(),
            },
        ],
    },
});
</script>

<template>
    <Head title="Dashboard" />

    <div
        class="flex h-full flex-1 flex-col gap-4 overflow-x-auto rounded-xl p-4"
    >
        <div class="grid auto-rows-min gap-4 md:grid-cols-3">
            {{ $page.props.permissions }}

            <Button
                v-if="$page.props.roles.includes('writer')"
                variant="outline"
            >
                Create User
            </Button>
            <!-- <div class="grid auto-rows-min gap-4 md:grid-cols-3">
                <Button v-if="can('user.create')" variant="outline">
                    Create User
                </Button>

                <Button v-if="can('user.edit')" variant="outline">
                    Edit User
                </Button>

                <Button v-if="can('user.delete')" variant="destructive">
                    Delete User
                </Button>
            </div> -->
            <div
                class="border-sidebar-border/70 dark:border-sidebar-border relative aspect-video overflow-hidden rounded-xl border"
            >
                <PlaceholderPattern />
            </div>
            <div
                class="border-sidebar-border/70 dark:border-sidebar-border relative aspect-video overflow-hidden rounded-xl border"
            >
                <PlaceholderPattern />
            </div>
            <div
                class="border-sidebar-border/70 dark:border-sidebar-border relative aspect-video overflow-hidden rounded-xl border"
            >
                <PlaceholderPattern />
            </div>
        </div>
        <div
            class="border-sidebar-border/70 dark:border-sidebar-border relative min-h-[100vh] flex-1 rounded-xl border md:min-h-min"
        >
            <PlaceholderPattern />
        </div>
    </div>
</template>
