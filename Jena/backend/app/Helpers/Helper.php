<?php

namespace App\Helpers;
use App\Category;

class Helper
{
    public static function implodeCategory($categories = array())
    {
        $store = array();
        foreach($categories as $category) {
            array_push($store, $category->category_id);
        }
        
        if (count($store) > 0) {
            return implode($store,',');
        }
        return '0';
    }
    public static function fetchCategory($categories = array())
    {
        $store = array();
        foreach($categories as $category) {
            array_push($store, $category->category_id);
        }
        
        if (count($store) > 0) {
            $dataResult = Category::fetchCategoryName($store);
            if($dataResult->count() > 0) {
                $spanTag = '';
                foreach ($dataResult as $catItem) {
                    $spanTag .= '<span class="badge badge-primary mr-1">'. $catItem->title .'</span>';
                }
                return $spanTag;
            }
        }
        return '';
    }
}