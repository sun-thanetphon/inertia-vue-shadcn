<script setup lang="ts">
import { Head, router } from "@inertiajs/vue3";
import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableFooter,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

import {
    Pagination,
    PaginationContent,
    PaginationEllipsis,
    PaginationItem,
    PaginationNext,
    PaginationPrevious,
} from "@/components/ui/pagination";

interface User {
    id: number;
    name: string;
    email: string;
    created_at: string;
}

interface UserPagination {
    data: User[];
    current_page: number;
    per_page: number;
    total: number;
    last_page: number;
}

const props = defineProps<{
    users: UserPagination;
}>();

defineOptions({
    layout: {
        breadcrumbs: [
            {
                title: "User",
                href: "/users",
            },
        ],
    },
});

const goToPage = (page: number) => {
    router.get(
        "/users",
        { page },
        {
            preserveState: true,
            preserveScroll: true,
        },
    );
};
</script>

<template>
    <Head title="User" />

    <div class="p-6 space-y-6">
        <Table>
            <TableCaption>A list of your system users.</TableCaption>

            <TableHeader>
                <TableRow>
                    <TableHead class="w-[100px]">ID</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead class="text-right">Joined Date</TableHead>
                </TableRow>
            </TableHeader>

            <TableBody>
                <TableRow v-for="user in users.data" :key="user.id">
                    <TableCell class="font-medium">
                        {{ user.id }}
                    </TableCell>

                    <TableCell>
                        {{ user.name }}
                    </TableCell>

                    <TableCell>
                        {{ user.email }}
                    </TableCell>

                    <TableCell class="text-right">
                        {{ user.created_at }}
                    </TableCell>
                </TableRow>
            </TableBody>

            <TableFooter>
                <TableRow>
                    <TableCell colspan="3"> Total Users </TableCell>

                    <TableCell class="text-right">
                        {{ users.total }} items
                    </TableCell>
                </TableRow>
            </TableFooter>
        </Table>

        <!-- Pagination -->
        <Pagination
            :items-per-page="users.per_page"
            :total="users.total"
            :default-page="users.current_page"
            @update:page="goToPage"
        >
            <PaginationContent>
                <PaginationPrevious />

                <template v-for="item in users.last_page" :key="item">
                    <PaginationItem
                        :value="item"
                        :is-active="item === users.current_page"
                        @click="goToPage(item)"
                    >
                        {{ item }}
                    </PaginationItem>
                </template>

                <PaginationNext />
            </PaginationContent>
        </Pagination>
    </div>
</template>
