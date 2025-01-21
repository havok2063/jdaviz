<template>
    <j-tray-plugin
      :config="config"
      plugin_key="MapViz"
      :api_hints_enabled.sync="api_hints_enabled"
      :description="docs_description"
      :uses_active_status="uses_active_status"
      @plugin-ping="plugin_ping($event)"
      :keep_active.sync="keep_active"
      :popout_button="popout_button"
      :scroll_to.sync="scroll_to">

      <div>
        <j-plugin-section-header>Maps</j-plugin-section-header>
        <v-row>
            <j-docs-link>Choose the input maps.</j-docs-link>
        </v-row>

        <plugin-file-import-select
        :items="mapfile_items"
        :selected.sync="mapfile_selected"
        label="Map"
        hint="Select a map to load."
        :from_file.sync="from_file"
        :from_file_message="from_file_message"
        dialog_title="Import Map"
        dialog_hint="Select a file containing a map"
        @click-cancel="file_import_cancel()"
        @click-import="file_import_accept()"
        >
        <g-file-import id="file-uploader"></g-file-import>
        </plugin-file-import-select>

        <v-btn @click="load_map()">Load Maps</v-btn>
        </div>

      <j-plugin-section-header>Available Maps</j-plugin-section-header>
    <v-row>
      <v-select
        :menu-props="{ left: true }"
        attach
        v-model="map_selected"
        :items="available_maps"
        @change="set_label()"
        label="Available Maps"
        hint="Select a map to load."
        persistent-hint
      ></v-select>
    </v-row>

    <plugin-add-results
      :label.sync="results_label"
      :label_default="results_label_default"
      :label_auto.sync="results_label_auto"
      :label_invalid_msg="results_label_invalid_msg"
      :label_overwrite="results_label_overwrite"
      label_hint="Label for the map"
      :add_to_viewer_items="add_to_viewer_items"
      :add_to_viewer_selected.sync="add_to_viewer_selected"
      action_label="Add Map"
      action_tooltip="Add the map data"
      :action_spinner="spinner"
      add_results_api_hint='plg.add_results'
      action_api_hint='plg.collapse(add_data=True)'
      @click:action="add_map"
    ></plugin-add-results>

    </j-tray-plugin>
</template>

