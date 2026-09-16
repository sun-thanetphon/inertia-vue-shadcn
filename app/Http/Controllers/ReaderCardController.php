<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Inertia\Inertia;

class ReaderCardController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return Inertia::render('ReaderCards/Index');
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        $cardData = null;
        $errorMessage = null;

        try {
            $response = Http::timeout(10)->get('http://localhost:8080/api/readers/read');

            if ($response->successful() && $response->json('status') === 'success') {
                $cardData = $response->json('data');
            } else {
                $errorMessage = $response->json('message') ?? 'เกิดข้อผิดพลาดในการอ่านบัตร';
            }
        } catch (\Exception $e) {
            $errorMessage = 'ไม่สามารถเชื่อมต่อกับ Service อ่านบัตรได้: ' . $e->getMessage();
        }

        return Inertia::render('ReaderCards/Index', [
            'cardData' => $cardData,
            'error' => $errorMessage
        ]);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
